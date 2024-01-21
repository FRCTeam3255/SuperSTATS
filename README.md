# Local install
pip install -e .

# Clear commit history
// Creating temp branch
- git checkout --orphan temp_branch

// Commit title
- git commit -am "Commit Title"

// Replacing old branch
- git branch -D branch-name
- git branch -m branch-name

// Pushing branch
- git push -f origin branch-name
- [MANUAL] publish branch
