git config --global user.email "forrest.collman@gmail.com"
git config --global user.name "CircleCi"
git config --global push.default matching
git checkout master
git merge dev
git push origin HEAD