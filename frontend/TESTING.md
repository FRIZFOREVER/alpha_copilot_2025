# Руководство по тестированию

## Быстрый старт

1. Установите зависимости:
```bash
cd frontend
npm install
```

2. Запустите тесты:
```bash
npm test
```

## Что было добавлено

### Зависимости
- `vitest` - тестовый фреймворк
- `@vitest/ui` - UI для тестов
- `@testing-library/react` - утилиты для тестирования React компонентов
- `@testing-library/jest-dom` - дополнительные матчеры для DOM
- `@testing-library/user-event` - симуляция пользовательских событий
- `jsdom` - браузерное окружение для тестов

### Конфигурация
- Настроен `vite.config.ts` для работы с Vitest
- Создан `src/test/setup.ts` для настройки тестового окружения

### Написанные тесты

#### Утилиты
- `chatHelpers.test.ts` - тесты для функций работы с чатами (getChatIcon, getChatInitial)
- `timeHelpers.test.ts` - тесты для форматирования времени (formatTime)
- `userHelpers.test.ts` - тесты для работы с пользователями (getUserInitials, getDisplayName, capitalizeFirst)

#### Хуки
- `useScrollBottom.test.ts` - тесты для хука автоматического скролла

#### Компоненты
- `messageList.test.tsx` - тесты для компонента списка сообщений

#### Функции
- `createStreamCallbacks.test.ts` - тесты для обработки стриминга сообщений

#### Схемы валидации
- `loginSchema.test.ts` - тесты для схемы валидации входа
- `registerSchema.test.ts` - тесты для схемы валидации регистрации

## Команды

- `npm test` - запуск тестов
- `npm run test:ui` - запуск тестов с UI интерфейсом
- `npm run test:coverage` - запуск тестов с покрытием кода

## Структура тестов

Тесты находятся рядом с тестируемыми файлами в папках `__tests__`:

```
src/
├── shared/
│   ├── lib/utils/__tests__/
│   └── hooks/__tests__/
├── features/
│   └── chat/ui/messageList/__tests__/
└── entities/
    ├── auth/lib/schemes/__tests__/
    └── chat/lib/__tests__/
```

## Примеры использования

### Тестирование утилит
```typescript
import { describe, it, expect } from "vitest";
import { myFunction } from "../myFunction";

describe("myFunction", () => {
  it("should work correctly", () => {
    expect(myFunction("input")).toBe("expected");
  });
});
```

### Тестирование React компонентов
```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MyComponent } from "../MyComponent";

describe("MyComponent", () => {
  it("should render correctly", () => {
    render(<MyComponent />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });
});
```

## Покрытие кода

После запуска `npm run test:coverage` отчет будет доступен в папке `coverage/`.

