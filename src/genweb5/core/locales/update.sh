#!/bin/bash

domain=genweb

../../../../../../bin/i18ndude rebuild-pot --pot $domain.pot --create $domain ../ \
../../../../../genweb5.theme/src/genweb5/theme/

../../../../../../bin/i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
