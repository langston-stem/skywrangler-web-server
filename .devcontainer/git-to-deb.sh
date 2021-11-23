# use git info to provide deb info

export DEBFULLNAME=$(git config user.name)
export DEBEMAIL=$(git config user.email)
