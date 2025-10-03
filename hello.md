git checkout -b feat/hello-world
echo "# Hello from P1T3" > hello.md
git add hello.md .github/workflows/ci.yml
git commit -m "chore: add hello.md and ci stub"
git push -u origin feat/hello-world
