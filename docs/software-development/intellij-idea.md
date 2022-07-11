# Intellij IDEA

## Setup

## Configuration

By default IDEA generates a bunch of configuration files that we don't want committed to git 
(e.g. modules.xml, runConfigurations.xml, vcs.xml, workspace.xml).

We don't want to necessarily pollute the repo gitignore file either with our local environment IDE files.

You can also create a global `.gitignore` file to define a list of rules for ignoring files in every Git repository on your computer. For example, you might create the file at `~/.gitignore_global` and add some rules to it.

In my case i want to ignore all IDEA generated files e.g. https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
(uncomment the Gradle/Maven section too)

```shell
git config --global core.excludesfile ~/.gitignore_global
```
