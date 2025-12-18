# Hookify

Локальный движок правил для Claude Code. Блокирует или предупреждает о нежелательных действиях.

## Быстрый старт

```bash
/hookify              # Создать правило (анализ разговора или инструкции)
/hookify:list         # Показать все правила
/hookify:configure    # Включить/выключить правила
/hookify:help         # Справка
```

**Правила:** `rules/*.local.md`

---

## Структура

```
.claude/
├── hooks/hookify/           # ← вы здесь
│   ├── engine/              # config_loader.py, rule_engine.py
│   ├── hooks/               # pretooluse.py, stop.py, etc.
│   └── rules/               # *.local.md — правила
├── commands/hookify/        # Slash-команды
├── skills/hookify/          # Skill для написания правил
└── agents/hookify-agents/   # conversation-analyzer agent
```

### Поток данных

```
Claude Code Event → hooks/*.py → config_loader → rule_engine → JSON response
```

**Важно:** Claude Code показывает `systemMessage` только если есть `hookSpecificOutput` с `permissionDecision`.

---

## Создание правил

### Структура файла

```markdown
---
name: rule-name
enabled: true
event: bash|file|stop|prompt
conditions:
  - field: command|file_path|new_text|user_prompt
    operator: regex_match|contains|equals|starts_with|ends_with|not_contains
    pattern: 'your-pattern'
action: block
---

**BLOCKED: Краткое описание**

Инструкция что делать вместо этого.

Do NOT делать X.
```

### Поля

| Поле | Описание |
|------|----------|
| `name` | Уникальное имя (kebab-case) |
| `enabled` | `true` / `false` |
| `event` | `bash`, `file`, `stop`, `prompt` |
| `conditions` | Список условий (AND-логика) |
| `action` | `block` (рекомендуется) или `warn` |

### События и поля

| Event | Поля для conditions |
|-------|---------------------|
| `bash` | `command` |
| `file` | `file_path`, `new_text`, `old_text` |
| `stop` | `reason` |
| `prompt` | `user_prompt` |

### Критичные правила синтаксиса

**1. Одинарные кавычки для regex:**
```yaml
pattern: 'npm\s+run\s+test'     # ✓
pattern: "npm\\s+run\\s+test"   # ✗
```

**2. Абсолютные пути в file_path:**
```yaml
pattern: '/backend/src/.*\.ts$'  # ✓ матчит /Users/.../backend/src/
pattern: 'backend/src/'          # ✗ не найдёт
```

**3. `block` вместо `warn`:**
- `warn` — Claude может проигнорировать
- `block` — принудительно останавливает

---

## Примеры

### Bash: Блокировка verbose тестов

```markdown
---
name: use-silent-tests
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'npm\s+run\s+test(?!.*:silent)(:unit|:integration|:e2e)?\s*$'
action: block
---

**BLOCKED: Use silent test command**

Replace: `npm run test` → `npm run test:silent`

Do NOT check package.json. Just use `:silent` variant.
```

### File: Блокировка console.log

```markdown
---
name: no-console-log
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/backend/src/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: 'console\.(log|warn|error)\('
action: block
---

**BLOCKED: Use NestJS Logger**

Replace with:
\`\`\`typescript
private readonly logger = new Logger(MyService.name);
this.logger.log('message');
\`\`\`
```

---

## Commands и Agents

### Slash-команды

| Команда | Описание |
|---------|----------|
| `/hookify [инструкция]` | Создать правило. Без аргументов — анализирует разговор |
| `/hookify:list` | Показать все правила с их статусом |
| `/hookify:configure` | Интерактивно включить/выключить правила |
| `/hookify:help` | Справка |

### Skill: hookify

Загружается командами автоматически. Содержит полный синтаксис правил.

**Файл:** `.claude/skills/hookify/SKILL.md`

### Agent: conversation-analyzer

Анализирует разговор для поиска паттернов фрустрации и ошибок.

**Файл:** `.claude/agents/hookify-agents/conversation-analyzer.md`

---

## Отладка

### Проверить загрузку правил

```bash
cd .claude/hooks/hookify
python3 -c "
import sys; sys.path.insert(0, 'engine')
from config_loader import load_rules

rules = load_rules(event='bash', cwd='$(pwd)')
print(f'Found {len(rules)} rules')
for r in rules: print(f'  {r.name}: enabled={r.enabled}')
"
```

### Проверить вывод хука

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"npm run test"},"hook_event_name":"PreToolUse","cwd":"'$(pwd)'"}' | \
  python3 .claude/hooks/hookify/hooks/pretooluse.py | python3 -m json.tool
```

**Ожидаемый вывод:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  },
  "systemMessage": "**[rule-name]**\n...",
  "continue": true
}
```

### Проверить что хуки вызываются

В выводе Claude Code:
```
Running PreToolUse hooks… (0/4 done)
 · PreToolUse:Bash: ...hookify.../hooks/pretooluse.py
```

Если hookify не в списке → проверьте `.claude/settings.local.json`.

### Troubleshooting

| Симптом | Причина | Решение |
|---------|---------|---------|
| Warning не показывается | Нет `hookSpecificOutput` | Проверьте rule_engine.py |
| Правила не найдены | Неверный путь | Правила в `rules/*.local.md` |
| Regex не матчит | Двойные кавычки | Используйте одинарные |
| File path не матчит | Относительный путь | Добавьте `/` в начало |

---

## Ограничения

1. **AND-логика условий** — для OR создавайте отдельные правила
2. **Простой YAML парсер** — без multiline strings
3. **Статичные паттерны** — нет переменных окружения
4. **Ручная регистрация** — хуки в `settings.local.json`

---

## Конфигурация

Хуки регистрируются в `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/pretooluse.py\"",
          "timeout": 10
        }]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/pretooluse.py\"",
          "timeout": 10
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/stop.py\"",
          "timeout": 10
        }]
      }
    ]
  }
}
```

---

## Wythm-фиксы

Исправления оригинального плагина:

| Проблема | Решение |
|----------|---------|
| Импорты `from hookify.core...` | `from core...` |
| Относительные пути | Параметр `cwd` |
| `systemMessage` не показывался | `hookSpecificOutput` |

---

*Migrated from global plugin: 2025-12-18*
