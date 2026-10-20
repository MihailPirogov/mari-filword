<?php
/* Мари филворд (mari-filword) — leaderboard API (PirogovLab). One file, JSON storage with flock, no DB.
 * Based on the «Марий мут» API (nickname filter copied from it).
 *   GET  ?a=board&period=week|all[&pid=..]       -> top 50 + own place
 *   POST {a:"name",  pid,key,name}               -> set / change nickname
 *   POST {a:"submit",pid,key,name?,total,week,wk,lv} -> report own score (cumulative)
 *   POST {a:"delete",pid,key}                    -> remove the player
 * Anti-cheat (sanity only; the game is offline so scores can't be proven):
 *   per-player secret key, rate limit per IP and per player, total never decreases, max growth per minute,
 *   total <= MAX_TOTAL, levels <= MAX_LEVELS, week <= total, week id = current ISO week only.
 */
declare(strict_types=1);
const TOP = 50, MAX_TOTAL = 2000000, MAX_LEVELS = 20000, MAX_RATE = 900;   // points per minute since previous submit
$DATA = getenv('FW_DATA') ?: '/var/www/www-root/data/mari-filword-private';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') { http_response_code(204); exit; }
function out(int $code, array $j): void { http_response_code($code); echo json_encode($j, JSON_UNESCAPED_UNICODE); exit; }
function jload(string $f, $def) { if (!is_file($f)) return $def; $j = json_decode((string)file_get_contents($f), true); return $j === null ? $def : $j; }
function jsave(string $f, $v): void { $tmp = $f . '.tmp' . getmypid(); file_put_contents($tmp, json_encode($v, JSON_UNESCAPED_UNICODE)); rename($tmp, $f); }
function lower(string $s): string { return mb_strtolower(trim($s), 'UTF-8'); }
function weekId(?int $t = null): string { return gmdate('o-\WW', ($t ?? time()) + 3 * 3600); }   // ISO week, Moscow time

/* ---------- nickname filter ---------- */
function nickProblem(string $name): ?string {
  global $DATA;
  $n = trim(preg_replace('/\s+/u', ' ', $name));
  $len = mb_strlen($n, 'UTF-8');
  if ($len < 2 || $len > 16) return 'Ник: от 2 до 16 символов';
  if (!preg_match('/^[\p{Cyrillic}A-Za-z0-9 _.\-]+$/u', $n)) return 'Можно буквы (кириллица, латиница), цифры, пробел, _ . -';
  if (!preg_match('/[\p{Cyrillic}A-Za-z]/u', $n)) return 'В нике нужна хотя бы одна буква';
  $low = lower($n);
  // fold look-alikes / leetspeak into Cyrillic, drop separators, collapse repeats
  $map = ['a'=>'а','b'=>'в','c'=>'с','e'=>'е','h'=>'н','k'=>'к','m'=>'м','o'=>'о','p'=>'р','t'=>'т','x'=>'х','y'=>'у','u'=>'и','n'=>'п','r'=>'г','3'=>'з','0'=>'о','4'=>'ч','6'=>'б','@'=>'а','ё'=>'е','й'=>'и','ӓ'=>'а','ӧ'=>'о','ӱ'=>'у','ӹ'=>'ы','ҥ'=>'н'];
  $cyr = preg_replace('/[^\p{Cyrillic}]/u', '', strtr($low, $map));
  $cyr = preg_replace('/(.)\1+/u', '$1', $cyr);
  // second fold: Latin transliteration (pizda, zhopa, mixed «пиzда»)
  $tr = strtr($low, ['zh'=>'ж','ch'=>'ч','sh'=>'ш','ya'=>'я','yu'=>'ю','a'=>'а','b'=>'б','v'=>'в','g'=>'г','d'=>'д','e'=>'е','z'=>'з','i'=>'и','k'=>'к','l'=>'л','m'=>'м','n'=>'н','o'=>'о','p'=>'п','r'=>'р','s'=>'с','t'=>'т','u'=>'у','f'=>'ф','h'=>'х','c'=>'ц','y'=>'ы','x'=>'х','j'=>'и','w'=>'в','q'=>'к','0'=>'о','3'=>'з','ё'=>'е','й'=>'и','ӓ'=>'а','ӧ'=>'о','ӱ'=>'у','ӹ'=>'ы','ҥ'=>'н']);
  $cyr .= '|' . preg_replace('/(.)\1+/u', '$1', preg_replace('/[^\p{Cyrillic}]/u', '', $tr));
  $lat = preg_replace('/[^a-z]/', '', strtr($low, ['0'=>'o','1'=>'i','3'=>'e','4'=>'a','5'=>'s','@'=>'a','$'=>'s','!'=>'i']));
  $ru = ['хуи','хуе','хуя','хую','пизд','пезд','бля','блиа','ебат','ебан','ебал','ебуч','ебну','ебл','уеб','заеб','выеб','поеб','разеб','мудак','мудил','пидор','пидар','педик','педр','гандон','гондон','залуп','шлюх','шалав','дроч','манда','жопа','жопу','жопе','сучк','сука','суки','сучар','шмар','говн','гавн','дерьм','срак','перд','дебил','уебок','урод','чмо','тварь','мраз','гнид','нацис','фашис','гитлер','хохол','ниггер','чурк','порн','секс','вагин','насил','убива','наркот','кокаин','гашиш','админ','модерат','пироговлаб'];
  $whitelist = ['корабл','оскорбля','сукно','скребл'];   // obvious false positives
  foreach ($whitelist as $w) $cyr = str_replace($w, '', $cyr);
  foreach ($ru as $r) if (mb_strpos($cyr, $r) !== false) return 'Этот ник нельзя использовать';
  $en = ['fuck','fuk','shit','bitch','cunt','dick','cock','pussy','whore','slut','nigg','fag','porn','sex','nazi','hitler','rape','pizd','pisd','huy','hui','xuy','xui','blya','blia','ebat','eban','ebal','yeban','suka','mudak','pidor','pidar','zhop','gandon','eblan','admin','moderat','pirogovlab','yandex','support'];
  foreach ($en as $r) if (strpos($lat, $r) !== false) return 'Этот ник нельзя использовать';
  $mhr = jload(__DIR__ . "/bad_mhr.json", []);
  if ($mhr) { $set = array_flip($mhr); foreach (preg_split('/[^\p{Cyrillic}]+/u', $low, -1, PREG_SPLIT_NO_EMPTY) as $tok) if (isset($set[$tok])) return 'Этот ник нельзя использовать'; }
  return null;
}


@mkdir($DATA, 0750, true);
$lock = fopen("$DATA/.lock", 'c');
function withLock(callable $f) { global $lock; flock($lock, LOCK_EX); try { return $f(); } finally { flock($lock, LOCK_UN); } }
function rateOk(string $bucket, int $max, int $win): bool {
  global $DATA; $f = "$DATA/rate.json"; $r = jload($f, []); $now = time();
  foreach ($r as $k => $ts) { $r[$k] = array_values(array_filter($ts, fn($t) => $t > $now - 3600)); if (!$r[$k]) unset($r[$k]); }
  $ts = array_filter($r[$bucket] ?? [], fn($t) => $t > $now - $win);
  if (count($ts) >= $max) { jsave($f, $r); return false; }
  $r[$bucket][] = $now; jsave($f, $r); return true;
}
function auth(array &$P, string $pid, string $key, bool $create): void {
  if (!preg_match('/^[a-f0-9]{32}$/', $pid) || !preg_match('/^[a-f0-9]{32}$/', $key)) out(400, ['ok' => false, 'err' => 'bad_id']);
  $kh = hash('sha256', $key);
  if (isset($P[$pid])) { if (!hash_equals($P[$pid]['kh'], $kh)) out(403, ['ok' => false, 'err' => 'bad_key']); return; }
  if (!$create) out(404, ['ok' => false, 'err' => 'no_player']);
  $P[$pid] = ['kh' => $kh, 'name' => null, 'total' => 0, 'lv' => 0, 'wk' => weekId(), 'week' => 0, 't' => time()];
}
function setName(array &$P, string $pid, string $name): void {
  $name = trim(preg_replace('/\s+/u', ' ', $name));
  if ($p = nickProblem($name)) out(422, ['ok' => false, 'err' => 'name', 'msg' => $p]);
  foreach ($P as $id => $p) if ($id !== $pid && $p['name'] !== null && lower($p['name']) === lower($name)) out(409, ['ok' => false, 'err' => 'name_taken', 'msg' => 'Этот ник уже занят']);
  $P[$pid]['name'] = $name;
}
$ip = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|fw');
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if ($method === 'GET') {
  $a = $_GET['a'] ?? 'board';
  if ($a === 'check') { $p = nickProblem((string)($_GET['name'] ?? '')); out(200, ['ok' => $p === null, 'msg' => $p]); }
  if ($a !== 'board') out(400, ['ok' => false, 'err' => 'bad_action']);
  $period = ($_GET['period'] ?? 'all') === 'week' ? 'week' : 'all'; $me = (string)($_GET['pid'] ?? ''); $wk = weekId();
  $rows = [];
  foreach (jload("$DATA/players.json", []) as $pid => $p) {
    if ($p['name'] === null) continue;
    $s = $period === 'week' ? ($p['wk'] === $wk ? $p['week'] : 0) : $p['total'];
    if ($s > 0) $rows[] = ['pid' => $pid, 'n' => $p['name'], 's' => $s, 'lv' => $p['lv'], 't' => $p['t']];
  }
  usort($rows, fn($x, $y) => [$y['s'], $x['t']] <=> [$x['s'], $y['t']]);
  $top = []; $mine = null;
  foreach ($rows as $i => $r) { $e = ['r' => $i + 1, 'n' => $r['n'], 's' => $r['s'], 'lv' => $r['lv'], 'me' => $r['pid'] === $me]; if ($i < TOP) $top[] = $e; if ($r['pid'] === $me) $mine = $e; }
  out(200, ['ok' => true, 'period' => $period, 'week' => $wk, 'top' => $top, 'me' => $mine, 'total' => count($rows)]);
}
if ($method !== 'POST') out(405, ['ok' => false, 'err' => 'method']);
$in = json_decode((string)file_get_contents('php://input', false, null, 0, 4096), true);
if (!is_array($in)) out(400, ['ok' => false, 'err' => 'bad_json']);
$pid = (string)($in['pid'] ?? ''); $key = (string)($in['key'] ?? ''); $act = (string)($in['a'] ?? '');
withLock(function () use ($in, $pid, $key, $act, $ip, $DATA) {
  if (!rateOk("ip:$ip", 60, 600) || !rateOk('p:' . substr($pid, 0, 32), 20, 600)) out(429, ['ok' => false, 'err' => 'rate', 'msg' => 'Слишком часто, попробуйте позже']);
  $P = jload("$DATA/players.json", []);
  if ($act === 'name') { auth($P, $pid, $key, true); setName($P, $pid, (string)($in['name'] ?? '')); jsave("$DATA/players.json", $P); out(200, ['ok' => true, 'name' => $P[$pid]['name']]); }
  if ($act === 'delete') { auth($P, $pid, $key, false); unset($P[$pid]); jsave("$DATA/players.json", $P); out(200, ['ok' => true]); }
  if ($act !== 'submit') out(400, ['ok' => false, 'err' => 'bad_action']);
  auth($P, $pid, $key, true);
  if (!empty($in['name']) && $in['name'] !== $P[$pid]['name']) setName($P, $pid, (string)$in['name']);
  if ($P[$pid]['name'] === null) out(422, ['ok' => false, 'err' => 'need_name', 'msg' => 'Сначала укажите ник']);
  $total = (int)($in['total'] ?? -1); $week = (int)($in['week'] ?? -1); $lv = (int)($in['lv'] ?? -1); $wk = (string)($in['wk'] ?? '');
  $p = &$P[$pid]; $now = time();
  if ($total < 0 || $total > MAX_TOTAL || $lv < 0 || $lv > MAX_LEVELS || $week < 0 || $week > $total) out(422, ['ok' => false, 'err' => 'bad_score']);
  if ($wk !== weekId()) { $week = 0; }
  if ($total < $p['total']) out(422, ['ok' => false, 'err' => 'decrease']);
  $mins = max(1, intdiv($now - $p['t'], 60) + 1);
  if ($p['total'] > 0 && $total - $p['total'] > MAX_RATE * $mins) out(422, ['ok' => false, 'err' => 'too_fast', 'msg' => 'Слишком быстрый рост очков']);
  if ($p['total'] === 0 && $total > MAX_RATE * 60) out(422, ['ok' => false, 'err' => 'too_much']);   // first report: at most ~1 h of play
  if ($p['wk'] !== weekId()) { $p['wk'] = weekId(); $p['week'] = 0; }
  $p['total'] = $total; $p['week'] = max($p['week'], min($week, $total)); $p['lv'] = max($p['lv'], $lv); $p['t'] = $now;
  jsave("$DATA/players.json", $P); out(200, ['ok' => true, 'total' => $p['total'], 'week' => $p['week']]);
});
