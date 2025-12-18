# Hookify Plugin Guide

Полное руководство по использованию плагина Hookify для Claude Code в проекте Wythm.

## Содержание

1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [Установка и настройка](#установка-и-настройка)
4. [Создание правил](#создание-правил)
5. [Синтаксис правил](#синтаксис-правил)
6. [Примеры правил](#примеры-правил)
7. [Отладка](#отладка)
8. [Известные ограничения](#известные-ограничения)

---

## Обзор

**Hookify** — плагин для Claude Code, позволяющий создавать кастомные правила-предупреждения, которые срабатывают при определённых действиях Claude.

### Для чего нужен

- Предотвращение опасных команд (`rm -rf`, `DROP TABLE`)
- Напоминания о стандартах кода
- Защита критичных файлов от случайных изменений
- Автоматические подсказки по workflow

### Как работает (высокоуровнево)

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Claude Code    │───▶│   Hookify    │───▶│  Rule Files     │
│  (hooks system) │    │  (Python)    │    │  (.local.md)    │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │                    │
         │                    ▼
         │              ┌──────────────┐
         │              │ Rule Engine  │
         │              │ (matching)   │
         │              └──────────────┘
         │                    │
         ▼                    ▼
┌─────────────────────────────────────────┐
│  Warning/Block message shown to user    │
└─────────────────────────────────────────┘
```

---

## Архитектура

### Компоненты (Project-Local Version)

После миграции с глобального плагина, hookify теперь полностью локален в проекте:

```
<project>/.claude/hooks/hookify/
├── engine/                   # Ядро движка правил
│   ├── __init__.py          # Экспорты модуля
│   ├── config_loader.py     # Загрузка и парсинг правил
│   └── rule_engine.py       # Оценка правил
├── hooks/                    # Python скрипты для каждого события
│   ├── __init__.py
│   ├── pretooluse.py        # Перед выполнением инструмента
│   ├── posttooluse.py       # После выполнения инструмента
│   ├── userpromptsubmit.py  # При отправке промпта
│   └── stop.py              # При остановке Claude
├── rules/                    # Правила (*.local.md)
│   └── *.local.md           # Файлы правил
├── docs/                     # Документация
│   └── hookify-guide.md     # Это руководство
└── README.md                 # Краткое описание
```

**Преимущества локальной версии:**
- Защита от перезаписи при обновлениях глобального плагина
- Полный контроль над кодом движка
- Версионирование вместе с проектом (при желании)

### Файлы правил

Правила хранятся в отдельной директории проекта:

```
<project>/.claude/hooks/hookify/
└── rules/
    ├── test-silent.local.md      # Блокировка verbose тестов
    ├── db-danger.local.md        # Блокировка опасных DB команд
    ├── arch-violation.local.md   # Защита архитектуры
    ├── dangerous-rm.local.md     # Защита от rm -rf
    ├── no-console.local.md       # Блокировка console.log
    ├── interface-naming.local.md # Проверка naming convention
    ├── pre-commit.local.md       # Чеклист перед коммитом
    └── schema-change.local.md    # Workflow для schema.prisma
```

**Паттерн именования:** `<rule-name>.local.md`

- `<rule-name>` — уникальное имя правила (kebab-case)
- `.local.md` — суффикс (`.local` означает не коммитить в git)

**Legacy-совместимость:** Плагин также поддерживает старый формат `hookify.*.local.md` в корне `.claude/` для обратной совместимости.

### Поток данных

```
1. Claude Code триггерит событие (PreToolUse, PostToolUse, etc.)
          │
          ▼
2. Вызывается соответствующий Python-хук
          │
          ▼
3. config_loader.py загружает правила из .claude/hooks/hookify/rules/*.local.md
          │
          ▼
4. rule_engine.py проверяет условия каждого правила
          │
          ▼
5. Если условия совпали → возвращается JSON с hookSpecificOutput + systemMessage
          │
          ▼
6. Claude Code показывает systemMessage пользователю (только если есть hookSpecificOutput!)
```

---

## Установка и настройка

### 1. Локальная версия (текущая)

Hookify теперь полностью локален в проекте. Проверить установку:
```bash
ls .claude/hooks/hookify/
# Должно показать: docs/ engine/ hooks/ rules/
```

### 2. Регистрация хуков

Хуки регистрируются в `.claude/settings.local.json`. Текущая конфигурация использует `$CLAUDE_PROJECT_DIR` для ссылок на локальные скрипты:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/userpromptsubmit.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/pretooluse.py\"",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/pretooluse.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/hookify/hooks/stop.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Ключевое отличие от глобального плагина:**
- Не нужен `CLAUDE_PLUGIN_ROOT` — скрипты находят engine через относительные пути
- Используется `$CLAUDE_PROJECT_DIR` для портабельности

### 3. Модификации плагина (Wythm-specific)

В оригинальном плагине были баги. Исправления:

#### a) Импорты (все хуки)

```python
# Было (не работало):
from hookify.core.config_loader import load_rules

# Стало (работает):
from core.config_loader import load_rules
```

#### b) Путь к правилам (config_loader.py)

```python
# Было (не находило файлы):
pattern = os.path.join('.claude', 'hookify.*.local.md')

# Стало (использует cwd из input):
project_dir = cwd or os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
pattern = os.path.join(project_dir, '.claude', 'hookify.*.local.md')
```

#### c) Передача cwd в хуках

```python
# Добавлено во все хуки:
cwd = input_data.get('cwd')
rules = load_rules(event=event, cwd=cwd)
```

#### d) Формат вывода для PreToolUse (rule_engine.py)

Claude Code требует полную структуру `hookSpecificOutput` для отображения предупреждений:

```python
# Было (не показывалось пользователю):
return {
    "systemMessage": combined_message
}

# Стало (показывается пользователю):
return {
    "hookSpecificOutput": {
        "hookEventName": hook_event,
        "permissionDecision": "allow",
        "permissionDecisionReason": "Hookify warning (operation allowed)"
    },
    "systemMessage": combined_message,
    "continue": True
}
```

---

## Создание правил

### Структура файла правила

```markdown
---
name: rule-name
enabled: true
event: bash|file|stop|prompt|all
conditions:
  - field: command|new_text|file_path|user_prompt
    operator: regex_match|contains|equals|starts_with|ends_with
    pattern: 'your-pattern-here'
action: warn|block
---

**Your Warning Title**

Your warning message in Markdown format.
Supports **bold**, `code`, lists, etc.
```

### Поля YAML frontmatter

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `name` | Да | Уникальное имя правила (kebab-case) |
| `enabled` | Да | `true` или `false` |
| `event` | Да | Тип события (см. ниже) |
| `conditions` | Да | Список условий для срабатывания |
| `action` | Нет | `block` (рекомендуется) или `warn`. В Wythm используется `block` для всех правил кроме prompt events |
| `tool_matcher` | Нет | Фильтр по инструменту (`Bash`, `Edit\|Write`) |

### Типы событий (event)

| Event | Когда срабатывает | Доступные поля |
|-------|-------------------|----------------|
| `bash` | Перед/после Bash команды | `command` |
| `file` | Перед/после Edit/Write | `file_path`, `new_text`, `old_text` |
| `prompt` | При отправке промпта | `user_prompt` |
| `stop` | При остановке Claude | `reason`, `transcript` |
| `all` | Всегда | Зависит от события |

### Операторы условий

| Оператор | Описание | Пример |
|----------|----------|--------|
| `regex_match` | Regex поиск | `'npm\s+run\s+test'` |
| `contains` | Содержит подстроку | `'console.log'` |
| `equals` | Точное совпадение | `'npm run test'` |
| `starts_with` | Начинается с | `'rm '` |
| `ends_with` | Заканчивается на | `'.env'` |
| `not_contains` | Не содержит | `':silent'` |

### Важно: Escape sequences в YAML

**Используйте одинарные кавычки** для паттернов с regex:

```yaml
# ПРАВИЛЬНО - одинарные кавычки:
pattern: 'npm\s+run\s+test'

# НЕПРАВИЛЬНО - двойные кавычки (нужно двойное экранирование):
pattern: "npm\\s+run\\s+test"
```

### Важно: Абсолютные пути в file_path

Claude Code передает **абсолютные пути** в поле `file_path`. Используйте `/` в начале паттерна:

```yaml
# ПРАВИЛЬНО - матчит /Users/.../backend/src/file.ts:
pattern: '/backend/src/.*\.ts$'

# НЕПРАВИЛЬНО - не найдёт абсолютный путь:
pattern: 'backend/src/.*\.ts$'
```

Аналогично для `command` — Claude может преобразовать относительный путь в абсолютный:
```yaml
# ПРАВИЛЬНО - матчит любой путь содержащий node_modules:
pattern: '\bnode_modules\b'

# НЕПРАВИЛЬНО - матчит только "rm -rf node_modules" буквально:
pattern: 'rm\s+-rf\s+node_modules'
```

---

## Примеры правил

### Принцип написания директивных сообщений

Сообщения должны быть **директивными**, чтобы Claude не тратил токены на исследование альтернатив:

1. **"BLOCKED:"** в заголовке — Claude сразу понимает что случилось
2. **Одна команда/действие** — не давать выбор, давать решение
3. **"Do NOT..."** в конце — явный запрет на лишние действия
4. **Без объяснений "почему"** — экономит токены и время

### 1. Блокировка verbose тестов

```markdown
---
name: use-silent-tests
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'npm\s+run\s+test(?!.*:silent)(?::unit|:integration|:e2e)?\s*$'
action: block
---

**BLOCKED: Use silent test command instead**

Replace your command with the `:silent` variant:
- `npm run test` → `npm run test:silent`
- `npm run test:unit` → `npm run test:unit:silent`

Do NOT search for scripts or check package.json. Just run the `:silent` version.
```

### 2. Блокировка опасных Prisma команд

```markdown
---
name: dangerous-db-operations
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'prisma\s+(migrate\s+reset|db\s+push|migrate\s+dev(?!.*--create-only))'
action: block
---

**BLOCKED: Dangerous Prisma command**

Use safe migration workflow instead:
\`\`\`bash
npm run prisma:migrate:dev -- --name <change_name> --create-only
npm run prisma:migrate:deploy
\`\`\`

Do NOT use `migrate reset`, `db push`, or `migrate dev` without `--create-only`.
```

### 3. Блокировка нарушений архитектуры

```markdown
---
name: architecture-layer-violation
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/src/core/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: "from\\s+['\"]@?infrastructure"
action: block
---

**BLOCKED: Infrastructure import in Core layer**

Core layer cannot import from Infrastructure. Use port interface instead.

Do NOT import PrismaService, Controllers, or @infrastructure in core files.
```

### 4. Pre-commit checklist (block)

```markdown
---
name: pre-commit-quality-gate
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'git\s+commit'
action: block
---

**BLOCKED: Run quality checks before commit**

Execute in backend/ directory:
\`\`\`bash
npm run format:check && npm run lint:check && npm run build && npm run test:silent
\`\`\`

Only commit after all checks pass.
```

### 5. Блокировка console.log

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
    pattern: 'console\.(log|warn|error|info|debug)\('
action: block
---

**BLOCKED: Use NestJS Logger instead of console.log**

Replace with:
\`\`\`typescript
private readonly logger = new Logger(MyService.name);
this.logger.log('message');
\`\`\`

Do NOT use console.log/warn/error/info/debug in backend code.
```

---

## Отладка

### Проверить загрузку правил

```bash
cd /path/to/wythm/.claude/hooks/hookify
python3 -c "
import sys
sys.path.insert(0, 'engine')
from config_loader import load_rules

cwd = '/path/to/wythm'
rules = load_rules(event='bash', cwd=cwd)
print(f'Found {len(rules)} bash rules:')
for r in rules:
    print(f'  - {r.name}: enabled={r.enabled}')
"
```

### Проверить matching правила

```bash
cd /path/to/wythm/.claude/hooks/hookify
python3 -c "
import sys
sys.path.insert(0, 'engine')
from config_loader import load_rules
from rule_engine import RuleEngine

cwd = '/path/to/wythm'
rules = load_rules(event='bash', cwd=cwd)
engine = RuleEngine()

test_input = {
    'tool_name': 'Bash',
    'tool_input': {'command': 'npm run test'},
    'hook_event_name': 'PreToolUse'
}

result = engine.evaluate_rules(rules, test_input)
print('Match result:', bool(result))
if result:
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
"
```

### Проверить полный вывод хука

```bash
cd /path/to/wythm
echo '{"tool_name": "Bash", "tool_input": {"command": "npm run test"}, "hook_event_name": "PreToolUse", "cwd": "'$(pwd)'"}' | \
  python3 .claude/hooks/hookify/hooks/pretooluse.py 2>&1 | python3 -m json.tool
```

Ожидаемый вывод для warn-правила:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Hookify warning (operation allowed)"
  },
  "systemMessage": "**[rule-name]**\nYour warning message...",
  "continue": true
}
```

### Проверить что хуки вызываются

В выводе Claude Code должны быть видны хуки:

```
Running PreToolUse hooks… (0/4 done)
 · PreToolUse:Bash: ...hookify.../hooks/pretooluse.py
```

Если hookify хук не появляется в списке — проверьте `settings.local.json`.

### Логи ошибок

Hookify пишет ошибки в stderr. Если правило не срабатывает:

1. Проверьте синтаксис YAML frontmatter
2. Проверьте regex паттерн
3. Убедитесь что `enabled: true`
4. Проверьте что `event` соответствует типу операции

### Troubleshooting: Warning не показывается

**Симптом:** Хук вызывается (видно в списке PreToolUse hooks), но предупреждение не появляется.

**Причины и решения:**

| Проблема | Решение |
|----------|---------|
| Отсутствует `hookSpecificOutput` | Убедитесь что rule_engine.py возвращает полную структуру (см. раздел "Модификации") |
| Неверный формат JSON | Проверьте вывод хука командой выше |
| cwd не передаётся | Убедитесь что хуки передают `cwd=input_data.get('cwd')` |
| Правила не найдены | Проверьте путь: `<project>/.claude/hooks/hookify/rules/*.local.md` |
| Двойное экранирование в regex | Используйте одинарные кавычки: `pattern: 'npm\s+test'` |

**Важно:** Claude Code показывает `systemMessage` пользователю **только** если в ответе есть валидный `hookSpecificOutput` с `permissionDecision`.

---

## Известные ограничения

### 1. Плагин не авто-регистрирует хуки

Claude Code плагины не имеют механизма автоматической регистрации хуков. Требуется ручная настройка в `settings.local.json`.

### 2. Простой YAML парсер

Hookify использует упрощённый YAML парсер, который:
- Не поддерживает сложные вложенные структуры
- Требует одинарных кавычек для regex паттернов
- Не поддерживает multiline strings

### 3. Условия работают как AND

Все условия в списке `conditions` должны совпасть (логическое AND). Для OR-логики создайте отдельные правила.

### 4. Нет поддержки переменных

Паттерны статичны, нельзя использовать переменные окружения или динамические значения.

---

## Команды плагина

```bash
# Список всех правил
/hookify:list

# Включить/выключить правила интерактивно
/hookify:configure

# Справка
/hookify:help

# Создать правило из анализа разговора
/hookify
```

---

## Файлы проекта

### Структура директории `.claude/hooks/hookify/`

```
.claude/hooks/hookify/
├── engine/                          # Движок правил
│   ├── __init__.py
│   ├── config_loader.py
│   └── rule_engine.py
├── hooks/                           # Python скрипты хуков
│   ├── __init__.py
│   ├── pretooluse.py
│   ├── posttooluse.py
│   ├── userpromptsubmit.py
│   └── stop.py
├── rules/                           # Все правила hookify (8 штук)
│   ├── test-silent.local.md         # Блокировка verbose тестов
│   ├── db-danger.local.md           # Блокировка опасных Prisma команд
│   ├── arch-violation.local.md      # Защита архитектурных слоёв
│   ├── no-console.local.md          # Блокировка console.log
│   ├── interface-naming.local.md    # Проверка naming convention
│   ├── pre-commit.local.md          # Чеклист перед коммитом
│   ├── dangerous-rm.local.md        # Защита от rm -rf
│   └── schema-change.local.md       # Workflow для schema.prisma
├── docs/
│   └── hookify-guide.md             # Эта документация
└── README.md
```

### Текущие правила Wythm (8 правил)

| Файл | Action | Назначение |
|------|--------|------------|
| `test-silent.local.md` | `block` | Блокирует `npm run test` без `:silent` |
| `db-danger.local.md` | `block` | Блокирует `prisma migrate reset`, `db push` и т.д. |
| `arch-violation.local.md` | `block` | Блокирует импорты infrastructure в core |
| `no-console.local.md` | `block` | Блокирует `console.log` в backend |
| `interface-naming.local.md` | `block` | Блокирует интерфейсы без `I` префикса |
| `pre-commit.local.md` | `block` | Блокирует `git commit` без прохождения чеклиста |
| `dangerous-rm.local.md` | `block` | Блокирует `rm -rf` на критичные пути |
| `schema-change.local.md` | `block` | Блокирует изменения schema.prisma без workflow |

### Конфигурация

- `.claude/settings.local.json` — регистрация хуков (не коммитить!)
- `.claude/hooks/hookify/rules/*.local.md` — файлы правил (не коммитить!)

---

## Сводка всех модификаций

Оригинальный плагин hookify имел несколько багов, которые были исправлены для работы в проекте Wythm:

| Файл | Проблема | Исправление |
|------|----------|-------------|
| `hooks/*.py` | Неверный путь импорта `from hookify.core...` | Заменён на `from core...` |
| `core/config_loader.py` | Относительный путь `.claude/` не находил файлы | Добавлен параметр `cwd` и использование абсолютного пути |
| `core/config_loader.py` | Не поддерживалась организация в подпапках | Добавлена поддержка `.claude/hookify/rules/*.local.md` |
| `hooks/*.py` | `cwd` не передавался в `load_rules()` | Добавлена передача `cwd=input_data.get('cwd')` |
| `core/rule_engine.py` | `systemMessage` без `hookSpecificOutput` не показывался | Добавлена полная структура с `permissionDecision: allow` |
| `core/rule_engine.py` | UserPromptSubmit использовал неверный формат | Добавлен `additionalContext` для инъекции в контекст Claude |
| `*.local.md` | Двойное экранирование в regex паттернах | Заменены двойные кавычки на одинарные |
| `*.local.md` | `action: warn` игнорировалось Claude | Изменено на `action: block` для принудительного соблюдения |

**Важно:** Эти изменения локальны для кэша плагина. При обновлении плагина изменения могут быть перезаписаны.

---

## warn vs block

| Режим | Поведение | Использование |
|-------|-----------|---------------|
| `warn` | Показывает сообщение, **разрешает** выполнение | Только для `prompt` events (Claude не может блокировать ввод пользователя) |
| `block` | Показывает сообщение, **блокирует** выполнение | Рекомендуется для всех остальных правил |

**Почему `block` предпочтительнее:**
- `warn` показывает сообщение, но Claude может его проигнорировать
- `block` гарантирует, что нежелательное действие не выполнится
- При `block` Claude вынужден использовать правильную альтернативу

---

## Контакты

При проблемах с плагином:
- Автор hookify: Daisy Hollman (Anthropic)
- Модификации для Wythm: см. этот документ

---

*Последнее обновление: 2025-12-18*
*Версия документа: 3.3 (добавлена документация про абсолютные пути, исправлены примеры)*
