Generated Bash and Zsh aliases export correction context before command
substitution, so the correction command sees the wrong alias environment.
Restore the shell-specific alias behavior while preserving existing history
settings.

Run the relevant tests, make the smallest complete source change, and leave the
working tree with the fix applied.
