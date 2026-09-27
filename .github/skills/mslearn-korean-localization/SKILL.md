---
name: mslearn-korean-localization
description: "Translate and maintain MicrosoftLearning-style course repositories in Korean by mirroring Instructions to Instructions-kr while preserving the English source, relative structure, technical identifiers, assets, links, and reproducible lab behavior. Use for requests to analyze, plan, translate, synchronize, validate, or publish Korean versions of repositories such as PL-7008, MS-4019, and AI-200."
license: MIT
metadata:
  author: hahaysh
  version: "1.0.0"
---

# Microsoft Learn Korean Lab Localization

Create and maintain a Korean mirror of the English `Instructions` tree in MicrosoftLearning-style course repositories.

For a reusable prompt that starts an initial course translation, see
[the course translation prompt](prompts/translate-course.md).

## Default layout

```text
Instructions/          # English source; never edit during localization
├─ Labs/
└─ media/

Instructions-kr/       # Korean mirror
├─ README.md           # Translation and synchronization record
├─ Labs/
└─ media/
```

Use these defaults unless repository inspection proves that the course uses different paths:

| Setting | Default |
|---|---|
| Source root | `Instructions` |
| Korean root | `Instructions-kr` |
| Source labs | `Instructions/Labs` |
| Korean labs | `Instructions-kr/Labs` |
| Source media | `Instructions/media` |
| Korean media | `Instructions-kr/media` |
| Translation README | `Instructions-kr/README.md` |
| Pages branch | Repository default branch |
| Pages source | Repository root |

## Determine the requested mode

Choose one mode from the user's request. Do not perform later modes implicitly.

| Intent | Mode |
|---|---|
| Analyze the repository or estimate scope | Analyze |
| Propose an approach without editing | Plan |
| Create the first Korean translation | Translate |
| Apply later English changes to Korean files | Synchronize |
| Check an existing translation | Validate |
| Publish the translated labs | Publish |

If the user says not to start work, remain in Analyze or Plan mode and make no changes.

Publishing, committing, and pushing require an explicit user request.

## Workflow

### 1. Inspect

Before editing:

1. Confirm the Git root, current branch, remote, and worktree status.
2. Locate source labs, media, downloadable assets, Jekyll configuration, and the site index.
3. Inventory Markdown files, front matter, headings, links, images, fenced blocks, and input values.
4. Preserve unrelated user changes. Never reset or overwrite them.
5. If the repository does not follow the expected structure, report the differences before translating.

### 2. Establish the translation contract

Create `Instructions-kr/README.md` from
[the template](templates/labs-kr-readme.md) when it does not exist.

Replace all template placeholders:

- `{{COURSE_CODE}}`
- `{{SOURCE_DIRECTORY}}`
- `{{TARGET_DIRECTORY}}`
- `{{SOURCE_COMMIT}}`
- `{{SYNC_DATE}}`
- `{{REPOSITORY}}`

Do not add YAML front matter to this README. It is a maintainer document and must not appear as a lab page.

### 3. Create or synchronize files

For an initial translation:

1. Create `Instructions-kr`.
2. Reproduce the relative directory structure from `Instructions`.
3. Create one Korean file for every translatable source Markdown file at the same relative path.
4. Copy referenced images and other required non-Markdown assets to the same relative paths.
5. Translate Markdown files while preserving their structure.
6. Never treat a directory whose name ends in `-kr` as English source content.

For synchronization:

1. Read the last synchronized source commit from the Korean README.
2. Compare that commit to the current source:

   ```powershell
   git diff <last-synchronized-commit>..HEAD -- Instructions
   ```

3. Classify additions, deletions, renames, and content changes.
4. Map each source path relative to `Instructions` onto the same path relative to `Instructions-kr`.
5. Apply Markdown changes semantically. Never replace an existing Korean Markdown file with the new English source.
6. Copy changed required binary assets to their mirrored paths.
7. Update the source commit and review date only after every change passes validation.

### 4. Translate

Translate for Korean learners, not sentence by sentence.

- Use natural instructional Korean.
- Use the `~합니다` style consistently.
- Preserve the meaning and required action of every step.
- Do not invent missing steps or silently repair source defects.
- Record source defects in the Korean README.
- Translate front matter values such as `title`, `module`, and `description`.
- Preserve front matter keys and structural values such as `duration`, `level`, and `islab`.
- Preserve heading levels, exercise/task numbering, lists, tables, callouts, links, images, and source code blocks.

### 5. Handle product and UI terms

Keep Microsoft product names in English:

- Microsoft Copilot Studio
- Microsoft Copilot
- Microsoft Entra ID
- Microsoft Teams
- Power Platform
- Power Apps
- Power Automate
- Dataverse
- OneDrive
- Excel Online (Business)
- Adaptive Card
- Power Fx

When screenshots use an English UI, show the Korean meaning followed by the UI label on first meaningful use:

```markdown
**에이전트(Agents)**
**지식(Knowledge)**
**도구(Tools)**
```

Avoid repeating both languages when the same control occurs many times in one short section.

### 6. Handle prompts

Both English and Korean prompts must be usable inputs. Put each language in its own copyable `prompt` block:

````markdown
다음 영문 또는 한국어 프롬프트 중 하나를 입력합니다.

```prompt
You are an agent that analyzes tasks.
```

```prompt
작업을 분석하는 에이전트입니다.
```
````

Rules:

- Preserve the English prompt exactly.
- Translate intent naturally rather than mechanically.
- Do not add a label such as `한국어 의미:`.
- Do not combine both languages in one block.
- Do not put Markdown emphasis or inline-code backticks inside the Korean prompt block unless those characters are part of the intended input.
- Preserve URLs, slash-inserted references, placeholders, and required identifiers in the Korean prompt.
- Keep explanations of formulas or URLs as prose; do not present them as alternative input prompts.

### 7. Handle human-readable input values

For names, titles, and descriptions that benefit from explanation, keep the exact input value in inline code and put Korean outside the code span:

```markdown
**`US Benefits Assistant`(미국 복리후생 지원 담당자)**
```

The learner enters only `US Benefits Assistant`. The Korean text is explanatory.

Do not apply this pattern to:

- Schema names
- Variable names
- URLs or GUIDs
- File paths
- Power Fx or Power Automate expressions
- OData filters
- API and connector identifiers
- Excel headers or choice values used by filters and expressions

When a human-readable name is referenced later, keep the operational English name unchanged.

### 8. Handle images, assets, and links

- Mirror required images and other non-Markdown assets from `Instructions` to the same relative paths under `Instructions-kr`.
- Preserve binary assets unchanged unless the user explicitly requests localized screenshots or files.
- Preserve image paths and translate alt text.
- Preserve link destinations and translate link text.
- Do not silently replace an upstream download URL.
- Report broken or stale links separately.
- Require every local target referenced by Korean Markdown to resolve from its mirrored location.

### 9. Validate

Run the bundled validator from the repository root:

```powershell
python .github\skills\mslearn-korean-localization\scripts\validate_translation.py --repo .
```

For a repository that still uses the legacy `Instructions/Labs-kr` layout, pass the paths explicitly:

```powershell
python .github\skills\mslearn-korean-localization\scripts\validate_translation.py `
  --repo . `
  --source Instructions\Labs `
  --target Instructions\Labs-kr `
  --readme Instructions\Labs-kr\README.md
```

Also run:

```powershell
git diff --check
git status --short
```

The validator must pass before reporting completion. Fix errors caused by the translation. Report unrelated pre-existing issues separately.

### 10. Publish with GitHub Pages

Only publish when explicitly requested.

For the standard layout:

1. Restrict the root `index.md` query to `/Instructions-kr/Labs/`.
2. Commit and push the translated files and index.
3. Resolve the repository name from `git remote`.
4. Confirm `gh auth status`.
5. Create Pages from the default branch root with `gh api`.
6. If Pages already exists, inspect and update it rather than trying to create it again.
7. Wait for the Pages build to reach `built`.
8. Verify the root page, every Korean lab URL, a representative image, and downloadable assets.

Expected lab URL:

```text
https://<owner>.github.io/<repository>/Instructions-kr/Labs/<lab>.html
```

Use GitHub CLI commands instead of requiring the user to change repository settings manually.

## Validation requirements

Before completion, verify:

- Source and Korean filenames correspond.
- Source and Korean Markdown relative paths correspond recursively.
- Every Korean lab contains Korean text.
- YAML front matter exists.
- Heading levels and ordered step structure match.
- Source image and link targets are preserved.
- Every source fenced block remains present in order.
- Korean prompts use separate `prompt` blocks.
- `한국어 의미` labels are absent.
- Technical identifiers remain unchanged.
- Local links and image paths resolve.
- Required referenced assets exist at the mirrored relative paths.
- `Instructions-kr/README.md` has no YAML front matter.
- Changes do not escape the approved scope.

## Completion report

Report:

- Files created or updated
- Translation and synchronization baseline
- Prompt and bilingual-value conventions applied
- Validator results
- Known source issues
- Whether changes were committed or pushed
- Pages URL and HTTP verification results when publishing
