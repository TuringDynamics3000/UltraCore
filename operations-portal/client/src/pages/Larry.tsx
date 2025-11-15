import { useState, useEffect, useRef } from "react";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Streamdown } from "streamdown";
import {
  MessageSquare,
  Send,
  Plus,
  Loader2,
  Bot,
  User,
  Wrench,
} from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";

/**
 * Larry Operations AI Chat Interface
 * 
 * Features:
 * - Streaming message responses
 * - Conversation history sidebar
 * - Tool execution indicators
 * - Markdown rendering
 * - Auto-scrolling message list
 */
export default function Larry() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch conversations
  const { data: conversations, refetch: refetchConversations } =
    trpc.larry.getConversations.useQuery(undefined, {
      enabled: isAuthenticated,
    });

  // Fetch messages for selected conversation
  const { data: messages, refetch: refetchMessages } =
    trpc.larry.getMessages.useQuery(
      { conversationId: selectedConversationId!, limit: 100 },
      {
        enabled: !!selectedConversationId,
      }
    );

  // Create conversation mutation
  const createConversation = trpc.larry.createConversation.useMutation({
    onSuccess: (data) => {
      setSelectedConversationId(data.conversationId);
      refetchConversations();
    },
  });

  // Send message mutation
  const sendMessage = trpc.larry.sendMessage.useMutation({
    onSuccess: () => {
      refetchMessages();
      setMessage("");
      setIsSending(false);
    },
    onError: (error) => {
      console.error("Failed to send message:", error);
      setIsSending(false);
    },
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Create first conversation on mount if none exist
  useEffect(() => {
    if (isAuthenticated && conversations && conversations.length === 0) {
      createConversation.mutate({});
    } else if (conversations && conversations.length > 0 && !selectedConversationId) {
      setSelectedConversationId(conversations[0].id);
    }
  }, [conversations, isAuthenticated]);

  const handleSendMessage = async () => {
    if (!message.trim() || !selectedConversationId || isSending) return;

    setIsSending(true);
    sendMessage.mutate({
      conversationId: selectedConversationId,
      message: message.trim(),
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewConversation = () => {
    createConversation.mutate({});
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <Bot className="w-16 h-16 text-muted-foreground" />
        <h1 className="text-2xl font-bold">Larry Operations AI</h1>
        <p className="text-muted-foreground">
          Please log in to chat with Larry
        </p>
        <Button asChild>
          <a href={getLoginUrl()}>Log In</a>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Conversation History Sidebar */}
      <div className="w-64 border-r border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <Button
            onClick={handleNewConversation}
            className="w-full"
            disabled={createConversation.isPending}
          >
            {createConversation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            New Conversation
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {conversations?.map((conv) => (
            <button
              key={conv.id}
              onClick={() => setSelectedConversationId(conv.id)}
              className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                selectedConversationId === conv.id
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent"
              }`}
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">
                    {conv.title || "New Conversation"}
                  </p>
                  <p className="text-xs opacity-70">
                    {new Date(conv.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Bot className="w-4 h-4" />
            <span>Larry Operations AI</span>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
              <Bot className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Larry</h1>
              <p className="text-sm text-muted-foreground">
                Operations AI Assistant
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!selectedConversationId ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <Bot className="w-16 h-16 text-muted-foreground" />
              <div>
                <h2 className="text-2xl font-bold mb-2">
                  Welcome to Larry Operations AI
                </h2>
                <p className="text-muted-foreground max-w-md">
                  I can help you query securities, analyze portfolios, monitor
                  RL agents, explore Kafka events, and access Data Mesh
                  products. Start a conversation to begin!
                </p>
              </div>
            </div>
          ) : messages && messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <Bot className="w-16 h-16 text-muted-foreground" />
              <div>
                <h2 className="text-xl font-bold mb-2">Start Chatting</h2>
                <p className="text-muted-foreground max-w-md">
                  Ask me anything about your operations data. Try:
                </p>
                <div className="mt-4 space-y-2">
                  <Card className="p-3 text-sm text-left hover:bg-accent cursor-pointer" onClick={() => setMessage("Show me the top 10 securities by market cap")}>
                    "Show me the top 10 securities by market cap"
                  </Card>
                  <Card className="p-3 text-sm text-left hover:bg-accent cursor-pointer" onClick={() => setMessage("What are the latest Kafka events?")}>
                    "What are the latest Kafka events?"
                  </Card>
                  <Card className="p-3 text-sm text-left hover:bg-accent cursor-pointer" onClick={() => setMessage("How are the RL agents performing?")}>
                    "How are the RL agents performing?"
                  </Card>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages?.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.role === "assistant" && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-primary-foreground" />
                    </div>
                  )}

                  <div
                    className={`max-w-[70%] ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    } rounded-lg p-4`}
                  >
                    {msg.role === "assistant" ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <Streamdown>{msg.content}</Streamdown>
                      </div>
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    )}

                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <div className="flex items-center gap-2 text-xs opacity-70">
                          <Wrench className="w-3 h-3" />
                          <span>
                            Used tools: {msg.toolCalls.join(", ")}
                          </span>
                        </div>
                      </div>
                    )}

                    <div className="mt-2 text-xs opacity-50">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>

                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5" />
                    </div>
                  )}
                </div>
              ))}

              {isSending && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        {selectedConversationId && (
          <div className="border-t border-border p-4">
            <div className="flex gap-2">
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask Larry anything about your operations..."
                className="min-h-[60px] max-h-[200px] resize-none"
                disabled={isSending}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!message.trim() || isSending}
                size="icon"
                className="h-[60px] w-[60px]"
              >
                {isSending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
