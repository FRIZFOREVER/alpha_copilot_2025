import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/shared/lib/mergeClass";

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export const MarkdownContent = ({
  content,
  className,
}: MarkdownContentProps) => {
  return (
    <div className={cn("markdown-content", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ ...props }) => (
            <h1
              className="text-2xl font-bold mt-4 mb-2 text-foreground first:mt-0"
              {...props}
            />
          ),
          h2: ({ ...props }) => (
            <h2
              className="text-xl font-bold mt-3 mb-2 text-foreground first:mt-0"
              {...props}
            />
          ),
          h3: ({ ...props }) => (
            <h3
              className="text-lg font-semibold mt-3 mb-2 text-foreground first:mt-0"
              {...props}
            />
          ),
          p: ({ ...props }) => (
            <p
              className="mb-3 last:mb-0 text-foreground leading-relaxed"
              {...props}
            />
          ),
          ul: ({ ...props }) => (
            <ul
              className="list-disc list-outside mb-3 ml-4 space-y-1 text-foreground"
              {...props}
            />
          ),
          ol: ({ ...props }) => (
            <ol
              className="list-decimal list-outside mb-3 ml-4 space-y-1 text-foreground"
              {...props}
            />
          ),
          li: ({ ...props }) => <li className="text-foreground" {...props} />,
          code: ({ className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !match;

            if (isInline) {
              return (
                <code
                  className="bg-gray-100 dark:bg-gray-800 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded text-sm font-mono"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ children, ...props }: any) => {
            return (
              <pre
                className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto mb-3 text-sm font-mono whitespace-pre-wrap"
                {...props}
              >
                {children}
              </pre>
            );
          },
          a: ({ ...props }) => (
            <a
              className="text-red-600 dark:text-red-400 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),
          strong: ({ ...props }) => (
            <strong className="font-bold text-foreground" {...props} />
          ),
          em: ({ ...props }) => (
            <em className="italic text-foreground" {...props} />
          ),
          hr: ({ ...props }) => (
            <hr
              className="my-4 border-gray-300 dark:border-gray-700"
              {...props}
            />
          ),
          blockquote: ({ ...props }) => (
            <blockquote
              className="border-l-4 border-gray-300 dark:border-gray-700 pl-4 my-3 italic text-gray-700 dark:text-gray-300"
              {...props}
            />
          ),
          table: ({ ...props }) => (
            <div className="overflow-x-auto my-3">
              <table
                className="min-w-full border-collapse border border-gray-300 dark:border-gray-700"
                {...props}
              />
            </div>
          ),
          thead: ({ ...props }) => (
            <thead className="bg-gray-100 dark:bg-gray-800" {...props} />
          ),
          tbody: ({ ...props }) => <tbody {...props} />,
          tr: ({ ...props }) => (
            <tr
              className="border-b border-gray-300 dark:border-gray-700"
              {...props}
            />
          ),
          th: ({ ...props }) => (
            <th
              className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-left font-semibold text-foreground"
              {...props}
            />
          ),
          td: ({ ...props }) => (
            <td
              className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-foreground"
              {...props}
            />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
