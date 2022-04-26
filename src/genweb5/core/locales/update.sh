#! /bin/bash

cd ../../../../../
./bin/i18ndude rebuild-pot \
  --pot src/genweb.core/genweb/core/locales/genweb.pot \
  --create genweb \
  src/genweb.banners/ src/genweb.controlpanel src/genweb.core \
  src/genweb.jsonify  src/genweb.logosfooter  src/genweb.migrations \
  src/genweb.packets  src/genweb.portlets     src/genweb.smartportlet \
  src/genweb.stack    src/genweb.theme        src/genweb.upc/

cd src/genweb.core/genweb/core/locales/
../../../../../bin/i18ndude sync --pot genweb.pot ca/LC_MESSAGES/genweb.po
../../../../../bin/i18ndude sync --pot genweb.pot es/LC_MESSAGES/genweb.po
../../../../../bin/i18ndude sync --pot genweb.pot en/LC_MESSAGES/genweb.po
