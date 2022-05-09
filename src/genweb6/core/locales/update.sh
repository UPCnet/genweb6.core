#!/bin/bash

domain=genweb

../../../../../../bin/i18ndude rebuild-pot --pot $domain.pot --create $domain ../ \
../../../../../genweb6.theme/src/genweb6/theme/

../../../../../../bin/i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
