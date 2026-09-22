# Installation globale (Windows)

Les fichiers de ce dossier sont testés et versionnés ici. Pour les activer
**globalement** sur ta machine Windows, copie-les dans `%USERPROFILE%\.claude\`
puis fusionne le bloc de configuration ci-dessous dans
`%USERPROFILE%\.claude\settings.json`.

## 1. Outils manquants (winget)

```powershell
winget install --id sharkdp.fd -e
winget install --id ast-grep.ast-grep -e
# deja presents en general : Git.Git, BurntSushi.ripgrep.MSVC, jqlang.jq, Python.Python.3.12
winget install --id MikeFarah.yq -e
```

Vérification :

```powershell
git --version; rg --version; fd --version; jq --version; yq --version; ast-grep --version; python --version
```

## 2. Copie des fichiers

```powershell
mkdir $env:USERPROFILE\.claude\hooks -Force
copy .claude\hooks\*.py   $env:USERPROFILE\.claude\hooks\
copy .claude\statusline.py $env:USERPROFILE\.claude\
```

## 3. Bloc à fusionner dans `%USERPROFILE%\.claude\settings.json`

Sous Windows, remplacer `python3` par `python` et `$CLAUDE_PROJECT_DIR/.claude`
par `%USERPROFILE%\.claude` (voir `settings.json` de ce dossier pour la
structure exacte des clés `statusLine`, `permissions.deny` et `hooks`).

> **Sauvegarde d'abord** : `copy $env:USERPROFILE\.claude\settings.json $env:USERPROFILE\.claude\settings.json.bak`

## 4. Vérification

```powershell
echo '{"tool_name":"Read","tool_input":{"file_path":"C:\\chemin\\gros.json"}}' | python $env:USERPROFILE\.claude\hooks\guard_read.py
```

Une décision `deny` avec une alternative `jq` confirme que le hook fonctionne.
