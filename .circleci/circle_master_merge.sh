git config --global user.email "forrest.collman@gmail.com"
git config --global user.name "CircleCi"
git config --global push.default matching
git checkout master
git merge dev -m "merging dev into master"
git push origin HEAD