# Gemini Plan Review Hook

Автоматическое ревью планов через Gemini CLI при выходе из plan mode.

## Интеграция с Plan Mode

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  User: "Спланируй добавление endpoint'а"                    │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude входит в Plan Mode                                  │
│  - Исследует codebase                                       │
│  - Создаёт план в tasks/plans/*.md                          │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude вызывает ExitPlanMode                               │
│  - tool_response содержит plan и filePath                   │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  PostToolUse Hook срабатывает                               │
│  - matcher: "ExitPlanMode"                                  │
│  - Запускает review-plan-gemini.sh                          │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Gemini CLI получает план (~30 сек)                         │
│  - Анализирует на security, architecture, edge cases        │
│  - Возвращает структурированное ревью                       │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Скрипт обновляет план файл                                 │
│  - Добавляет "## Gemini Review" секцию                      │
│  - Возвращает additionalContext для Claude                  │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude получает результат и может:                         │
│  - Учесть замечания Gemini                                  │
│  - Предупредить пользователя о проблемах                    │
│  - Продолжить имплементацию с учётом ревью                  │
└─────────────────────────────────────────────────────────────┘
```

### Данные из ExitPlanMode

Hook получает JSON со следующей структурой:

```json
{
  "tool_name": "ExitPlanMode",
  "tool_response": {
    "plan": "# План: ...\n\n## Steps\n...",
    "filePath": "/path/to/tasks/plans/plan-name.md",
    "isAgent": false
  }
}
```

- `plan` — полный текст плана (markdown)
- `filePath` — путь к файлу плана на диске
- `isAgent` — был ли план создан агентом

### Почему PostToolUse, а не PreToolUse?

- **PostToolUse** — план уже сохранён, можно безопасно добавить ревью
- **PreToolUse** — заблокировал бы выход из plan mode до завершения Gemini
- Текущий подход: план сохраняется мгновенно, ревью добавляется асинхронно

## Как работает

1. Claude создаёт план и вызывает `ExitPlanMode`
2. PostToolUse hook запускает `.claude/scripts/review-plan-gemini.sh`
3. Скрипт отправляет план в Gemini CLI для ревью
4. Gemini анализирует план на:
   - Security issues (auth, validation, injection)
   - Performance problems (N+1 queries, missing indexes)
   - DDD/Clean Architecture violations
   - Missing edge cases and error handling
   - Testability concerns
5. Review добавляется в файл плана как секция `## Gemini Review`

## Конфигурация

**Файл**: `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/scripts/review-plan-gemini.sh",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

## Скрипт

**Путь**: `.claude/scripts/review-plan-gemini.sh`

Скрипт:
- Читает план из `tool_response.plan`
- Формирует промпт с контекстом проекта (NestJS, DDD, Clean Architecture)
- Вызывает `gemini --model gemini-3-pro-preview` с one-shot промптом
- Парсит ответ и добавляет в план файл
- Возвращает `additionalContext` для Claude

## Характеристики

| Параметр | Значение |
|----------|----------|
| Timeout | 300 секунд |
| Модель | gemini-3-pro-preview |
| Среднее время | ~30-40 секунд |
| Блокирует Claude | Нет (graceful degradation) |

## Error Handling

При любой ошибке hook возвращает `exit 0` и не блокирует работу:

- Gemini недоступен → `{"systemMessage": "Gemini review failed"}`
- Rate limit → `{"systemMessage": "Gemini review skipped: rate limit"}`
- Пустой ответ → `{"systemMessage": "Gemini review empty"}`
- Timeout → hook прерывается, Claude продолжает

## Пример вывода

После `ExitPlanMode` в план добавляется:

```markdown
---

## Gemini Review

_Generated: 2026-01-22 14:53:05_

### Summary
The plan violates Clean Architecture principles by implying data access directly in Controller.

### Issues Found
- **DDD/Clean Architecture Violation (HIGH):** Controllers must delegate to Use Cases
- **Security/Auth Missing (MEDIUM):** Lacks Authentication guards

### Recommendations
- Implement via Use Case: Create `GetUserByIdUseCase`
- Define DTOs for Request/Response
- Enforce Auth guards explicitly
```

## Требования

- Gemini CLI установлен: `npm install -g @google/gemini-cli`
- Аутентификация настроена: `gemini` (интерактивно) или `GEMINI_API_KEY`
- jq установлен для парсинга JSON

## Отладка

```bash
# Проверить логи (если включено)
cat /tmp/gemini-hook-debug.log

# Тест Gemini напрямую
gemini --model gemini-3-pro-preview "Say hello" --output-format text

# Проверить конфиг hook
jq '.hooks.PostToolUse' .claude/settings.json
```

---

**Создан**: 2026-01-22
