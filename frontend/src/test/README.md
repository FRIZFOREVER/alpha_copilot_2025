# Unit Tests

Этот проект использует [Vitest](https://vitest.dev/) и [React Testing Library](https://testing-library.com/react) для unit тестирования.

## Установка зависимостей

```bash
npm install
```

## Запуск тестов

### Запуск всех тестов
```bash
npm test
```

### Запуск тестов в watch режиме
```bash
npm test -- --watch
```

### Запуск тестов с UI
```bash
npm run test:ui
```

### Запуск тестов с покрытием кода
```bash
npm run test:coverage
```

## Структура тестов

Тесты организованы рядом с тестируемыми файлами:

```
src/
├── shared/
│   ├── lib/
│   │   └── utils/
│   │       ├── chatHelpers.ts
│   │       └── __tests__/
│   │           └── chatHelpers.test.ts
│   └── hooks/
│       ├── useScrollBottom.ts
│       └── __tests__/
│           └── useScrollBottom.test.ts
├── features/
│   └── chat/
│       └── ui/
│           └── messageList/
│               ├── messageList.tsx
│               └── __tests__/
│                   └── messageList.test.tsx
└── entities/
    └── chat/
        └── lib/
            ├── createStreamCallbacks.ts
            └── __tests__/
                └── createStreamCallbacks.test.ts
```

## Написанные тесты

### Утилиты
- ✅ `chatHelpers.test.ts` - тесты для функций работы с чатами
- ✅ `timeHelpers.test.ts` - тесты для форматирования времени
- ✅ `userHelpers.test.ts` - тесты для работы с пользователями

### Хуки
- ✅ `useScrollBottom.test.ts` - тесты для хука автоматического скролла

### Компоненты
- ✅ `messageList.test.tsx` - тесты для компонента списка сообщений

### Функции
- ✅ `createStreamCallbacks.test.ts` - тесты для обработки стриминга сообщений

### Схемы валидации
- ✅ `loginSchema.test.ts` - тесты для схемы валидации входа
- ✅ `registerSchema.test.ts` - тесты для схемы валидации регистрации

## Написание новых тестов

При создании нового теста следуйте этим правилам:

1. Создайте папку `__tests__` рядом с тестируемым файлом
2. Назовите тестовый файл как `[имя-файла].test.ts` или `[имя-файла].test.tsx`
3. Используйте `describe` для группировки тестов
4. Используйте `it` или `test` для отдельных тестов
5. Используйте `expect` для проверок

### Пример

```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../myFunction";

describe("myFunction", () => {
  it("should return expected value", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```

## Конфигурация

Конфигурация тестов находится в `vite.config.ts` в секции `test`.

Основные настройки:
- `globals: true` - глобальные функции (describe, it, expect)
- `environment: "jsdom"` - браузерное окружение для тестирования React компонентов
- `setupFiles: ["./src/test/setup.ts"]` - файл с настройками перед запуском тестов

