/**
 * Получает цвет иконки чата на основе его ID
 * @param chatId - ID чата
 * @returns CSS класс цвета для иконки
 */
export const getChatIcon = (chatId: string): string => {
  const colors = [
    "bg-blue-500",
    "bg-purple-500",
    "bg-green-500",
    "bg-orange-500",
    "bg-pink-500",
    "bg-indigo-500",
  ];
  const index = parseInt(chatId) % colors.length;
  return colors[index];
};

/**
 * Получает первую букву названия чата для иконки
 * @param title - Название чата
 * @returns Первая буква в верхнем регистре
 */
export const getChatInitial = (title: string): string => {
  return title.charAt(0).toUpperCase();
};
