# The following are a set of guidelines for contributing to this repository


# 1. Commit messages
A commit message should fall in one of below tags 
- feat : Features  : A new feature
- fix	 : Bug Fixes : A bug fix
- docs : Documentation : Documentation only changes
- style :	Styles : Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- refactor : Code Refactoring : A code change that neither fixes a bug nor adds a feature
- perf : Performance Improvements : A code change that improves performance
- test : Tests : Adding missing tests or correcting existing tests
- build : Builds : Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- ci : Continuous Integrations : Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- chore : Chores : Other changes that don't modify src or test files
- revert : Reverts : Reverts a previous commit

In general, try to stick to https://www.conventionalcommits.org/en/v1.0.0/#specification

# 2. Preparing a MR

Before pushing a MR, kindly cleanup the commit history. You can do a `git rebase -i` such that intermediate commits 
t   hat do not add value to the history of the commits that do not show up in the merged history

# 3. JIRA ID

If your commit / MR is related to a JIRA include the JIRA ID in the commit message

for example: If the commit adds a "debug feature" and is realted to JIR-167 and the commit id should looke like

```bash
 feat:[JIR-167] Added debug feature
 ```

# 4. Tests 

Your MR should include unit tests and integration tests for the feature, if it applies and should be passing them

# 5. Review

Please ensure that a self review of the MR has happened before asking another person to review it. Be mindful of other people's time.