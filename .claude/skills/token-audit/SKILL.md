---
name: token-audit
description: Mesure le contexte permanent d'une config Claude Code et décide quoi installer, garder ou supprimer. À utiliser avant d'ajouter une Skill, un hook, un serveur MCP ou un repo tiers censé "économiser des tokens".
---

# Token audit

## 1. Mesurer avant de juger

```bash
python3 .claude/skills/token-audit/audit.py <chemin_projet>
```

Sortie : coût permanent par poste, et coût au chargement pour les Skills.
Compléter avec `/context` pour les connecteurs claude.ai, invisibles au script.

Ne jamais raisonner sur une annonce marketing ("−90 %"). Mesurer, ou se taire.

## 2. Test de bénéfice net

Un candidat (Skill, hook, MCP, repo) n'est adopté que s'il passe les quatre :

| Critère | Rejet si |
|---|---|
| **Coût permanent** | ajoute > 300 tokens à chaque tour |
| **Déterminisme** | se contente de *suggérer* au modèle d'être sobre |
| **Non-duplication** | recouvre un hook ou une règle déjà en place |
| **Gain mesurable** | aucun avant/après reproductible ne peut être produit |

Un serveur **MCP** échoue presque toujours le premier critère : ses noms d'outils
et ses instructions sont rechargés à chaque tour. Un outil « d'économie » livré
en MCP est net négatif sauf preuve contraire chiffrée.

## 3. Hiérarchie des leviers

Par gain décroissant réel :

1. **Retirer les connecteurs MCP inutiles** — ~1 500–2 500 tokens/tour chacun.
2. **Hooks déterministes** (`PreToolUse`) — refusent la lecture ou le dump avant
   qu'il n'atteigne le modèle. Coût permanent nul.
3. **`/compact`** sur session longue — 10–20k → 1–3k.
4. **Règles CLAUDE.md** courtes — comportemental, donc faillible ; garder < 300 tokens.
5. **Skills** — seulement pour une vraie procédure longue et réutilisable ;
   la description est permanente, le corps ne l'est pas.

Ce qui ne fait *rien* gagner : les outils de mesure d'usage (`ccusage` et
équivalents). Ils informent, ils n'économisent pas.

## 4. Décision

Après mesure, produire un verdict par candidat :

`ADOPTÉ` (gain chiffré) · `REJETÉ` (critère échoué, lequel) · `À MESURER` (essai requis)

Puis réexécuter `audit.py` pour vérifier que le total permanent n'a pas grossi.

## 5. Code tiers

Ne jamais cloner ni exécuter un repo tiers dans la config de l'utilisateur sans
son accord explicite. Lire la source (WebFetch), extraire l'idée, réimplémenter
localement. Un gain de tokens ne justifie pas une dépendance non auditée.
