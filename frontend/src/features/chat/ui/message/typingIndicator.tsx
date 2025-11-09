export const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-1.5 py-1">
      <div className="flex gap-1.5">
        <div 
          className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" 
          style={{ animationDelay: "0ms", animationDuration: "1.4s" }}
        />
        <div 
          className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" 
          style={{ animationDelay: "200ms", animationDuration: "1.4s" }}
        />
        <div 
          className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce" 
          style={{ animationDelay: "400ms", animationDuration: "1.4s" }}
        />
      </div>
    </div>
  );
};

