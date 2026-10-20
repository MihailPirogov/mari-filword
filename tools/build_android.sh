#!/bin/bash
# Signed release APK + AAB of «Мари филворд» -> release/mari-filword.apk, release/mari-filword.aab (package ru.pirogovlab.marifilword)
# Own release key: release/keys/ (backup in the bot store, see release/keys/README_KEYS.txt). Ad unit IDs: android/app/src/main/res/values/ads.xml
set -euo pipefail
cd /workspace/mari-filword
python3 tools/build_release.py android
export JAVA_HOME=${JAVA_HOME_17:-/home/box/jdk17}; export PATH=$JAVA_HOME/bin:$PATH
export ANDROID_HOME=${ANDROID_HOME:-/home/box/android-sdk}
GRADLE=${GRADLE:-/home/box/gradle-8.13/bin/gradle}
(cd android && $GRADLE --no-daemon -q clean assembleRelease bundleRelease)
cp android/app/build/outputs/apk/release/app-release.apk release/mari-filword.apk
cp android/app/build/outputs/bundle/release/app-release.aab release/mari-filword.aab
BT=$ANDROID_HOME/build-tools/36.0.0
$BT/apksigner verify --print-certs release/mari-filword.apk | grep -E "SHA-256|DN" && echo "apk signature OK"
$BT/aapt2 dump badging release/mari-filword.apk | grep -E "^package|minSdk|targetSdk|application-label:|application-label-en:"
echo "ad units: $(grep -o 'name="ad_[a-z]*_id"[^>]*>[^<]*' android/app/src/main/res/values/ads.xml | sed 's/.*>//' | tr '\n' ' ')"
ls -la release/mari-filword.apk release/mari-filword.aab
