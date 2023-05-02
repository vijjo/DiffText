

**Delete trailing tab at the end of line**
```Regex
[\t ]+\n
```
```Regex
\n
```

**Remove all the tabs in the first separation:**
```Regex
^([\w ’‘"“”\-—;:,=\.>]*) ?[\t ]+(adj|n|v|ind|pp|prp|ptp|pn|pr\.|pt\.)(.*(?=\t).*)$
```
```Regex
$1\t$2$3
```

**Remove tab in the middle of line:**
```Regex
(\n[^\t\n]*)\t+([^\n\t]*\n\n)
```
```Regex
$1 $2
```

**Remove 6 tabs or more with space:**
```Regex
\t{6,}
```
```Regex
 
```

**Remove space tab with tab:**
```Regex
 \t
```
```Regex
\t
```

**Remove all extra spaces:**
```Regex
 {2,}
```

**Remove 2+ tabs with two tabs when they are after pos and there's no grammar:**
```Regex
(adj|n|v|ind|pp|prp|ptp|pn|pr\.|pt\.|v\. ?refl) ?\t{2,}([^\t\n]*)$
```
```Regex
$1\t\t$2
```

**Remove 2+ tabs after grammar:**
```
(\t(?:f\.|ac\.|s\.|voc\.|neg|pr\.|pl|ins\.|adv|aor\.|dat\.|loc|inf|abl\.|abs|fut\.|m\.|conj|n\.|nt\.|gen\.|loc\.|opt\.|ac\.|3\.|2\.|1\.){1,}s?)\t{2,}([^\t\n]*)$
```
```
$1\t$2
```

**Remove 2+ tabs between pos and grammar:**
```
\t{2,}((?:f\.|ac\.|s\.|voc\.|neg|pr\.|pl|ins\.|adv|aor\.|dat\.|loc|inf|abl\.|abs|fut\.|m\.|n\.|nt\.|gen\.|loc\.|conj||opt\.|ac\.|3\.|2\.|1\.){1,}s?)
```
```
\t$1
```
