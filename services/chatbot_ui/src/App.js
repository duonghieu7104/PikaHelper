import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Send, Bot, User, Loader, MessageSquare, Trash2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  overflow: hidden;
`;

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
`;

const Subtitle = styled.p`
  margin: 5px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
`;

const ClearButton = styled.button`
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  transition: background 0.2s;

  &:hover {
    background: rgba(255,255,255,0.3);
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const Message = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? '#667eea' : '#764ba2'};
  color: white;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  max-width: 70%;
  padding: 15px 20px;
  border-radius: 20px;
  background: ${props => props.isUser ? '#667eea' : 'white'};
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  word-wrap: break-word;

  h1, h2, h3, h4, h5, h6 {
    margin: 0 0 10px 0;
    color: ${props => props.isUser ? 'white' : '#333'};
  }

  p {
    margin: 0 0 10px 0;
    line-height: 1.6;
  }

  ul, ol {
    margin: 10px 0;
    padding-left: 20px;
  }

  li {
    margin: 5px 0;
  }

  code {
    background: ${props => props.isUser ? 'rgba(255,255,255,0.2)' : '#f1f3f4'};
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
  }

  pre {
    background: ${props => props.isUser ? 'rgba(255,255,255,0.2)' : '#f1f3f4'};
    padding: 10px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 10px 0;
  }
`;

const SourcesContainer = styled.div`
  margin-top: 10px;
  padding: 10px;
  background: ${props => props.isUser ? 'rgba(255,255,255,0.1)' : '#f8f9fa'};
  border-radius: 10px;
  border-left: 3px solid #667eea;
`;

const SourceItem = styled.div`
  font-size: 12px;
  margin: 5px 0;
  opacity: 0.8;
`;

const ImageContainer = styled.div`
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

const ImageItem = styled.img`
  max-width: 200px;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const LinkContainer = styled.div`
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

const LinkItem = styled.a`
  color: #667eea;
  text-decoration: none;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 15px;
  font-size: 12px;
  transition: all 0.2s;
  cursor: pointer;
  display: inline-block;
  border: 1px solid rgba(102, 126, 234, 0.3);
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    text-decoration: underline;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  background: white;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 10px;
  align-items: flex-end;
`;

const Input = styled.textarea`
  flex: 1;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  padding: 15px 20px;
  font-size: 16px;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  min-height: 20px;
  max-height: 120px;

  &:focus {
    border-color: #667eea;
  }

  &::placeholder {
    color: #adb5bd;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 15px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  width: 50px;
  height: 50px;

  &:hover {
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6c757d;
  font-style: italic;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
`;

const WelcomeTitle = styled.h2`
  margin: 0 0 10px 0;
  color: #495057;
`;

const WelcomeText = styled.p`
  margin: 0;
  line-height: 1.6;
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Generate session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input.trim(),
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        sources: data.sources || [],
        images: data.images || [],
        links: data.links || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    if (!sessionId) return;

    try {
      await fetch(`${API_BASE_URL}/chat/history/${sessionId}`, {
        method: 'DELETE'
      });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    return content;
  };

  return (
    <AppContainer>
      <ChatContainer>
        <Header>
          <Title>PikaHelper Chatbot</Title>
          <Subtitle>Trợ lý AI chuyên về hướng dẫn game PokeMMO</Subtitle>
          <ClearButton onClick={clearChat}>
            <Trash2 size={16} />
            Xóa lịch sử
          </ClearButton>
        </Header>

        <MessagesContainer>
          {messages.length === 0 ? (
            <WelcomeMessage>
              <WelcomeTitle>Chào mừng đến với PikaHelper!</WelcomeTitle>
              <WelcomeText>
                Tôi là trợ lý AI chuyên về hướng dẫn game PokeMMO. Tôi có thể giúp bạn:
                <br />• Hướng dẫn tải và cài đặt game
                <br />• Hướng dẫn hoàn thành cốt truyện
                <br />• Tư vấn về PvP và xây dựng đội hình
                <br />• Hướng dẫn kiếm tiền trong game
                <br />• Và nhiều hơn nữa!
                <br /><br />Hãy đặt câu hỏi để bắt đầu!
              </WelcomeText>
            </WelcomeMessage>
          ) : (
            messages.map((message, index) => (
              <Message key={index} isUser={message.role === 'user'}>
                <MessageAvatar isUser={message.role === 'user'}>
                  {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </MessageAvatar>
                <MessageContent isUser={message.role === 'user'}>
                  <ReactMarkdown>{formatMessage(message.content)}</ReactMarkdown>

                  {/* Display images if available */}
                  {message.images && message.images.length > 0 && (
                    <ImageContainer>
                      {message.images.map((image, idx) => (
                        <ImageItem
                          key={idx}
                          src={image}
                          alt={`Image ${idx + 1}`}
                          onClick={() => window.open(image, '_blank')}
                        />
                      ))}
                    </ImageContainer>
                  )}

                  {/* Display links if available */}
                  {message.links && message.links.length > 0 && (
                    <LinkContainer>
                      {message.links.map((link, idx) => (
                        <LinkItem
                          key={idx}
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => {
                            e.preventDefault();
                            window.open(link, '_blank', 'noopener,noreferrer');
                          }}
                        >
                          🔗 {link.length > 50 ? link.substring(0, 50) + '...' : link}
                        </LinkItem>
                      ))}
                    </LinkContainer>
                  )}

                  {message.sources && message.sources.length > 0 && (
                    <SourcesContainer isUser={message.role === 'user'}>
                      <strong>Nguồn tham khảo:</strong>
                      {message.sources.map((source, idx) => (
                        <SourceItem key={idx}>
                          {source.source_id}. {source.file_name} (Độ tin cậy: {(source.score * 100).toFixed(1)}%)
                        </SourceItem>
                      ))}
                    </SourcesContainer>
                  )}
                </MessageContent>
              </Message>
            ))
          )}

          {isLoading && (
            <Message>
              <MessageAvatar>
                <Bot size={20} />
              </MessageAvatar>
              <MessageContent>
                <LoadingMessage>
                  <Loader size={16} className="animate-spin" />
                  Đang suy nghĩ...
                </LoadingMessage>
              </MessageContent>
            </Message>
          )}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập câu hỏi của bạn về PokeMMO..."
            disabled={isLoading}
            rows={1}
          />
          <SendButton onClick={sendMessage} disabled={!input.trim() || isLoading}>
            <Send size={20} />
          </SendButton>
        </InputContainer>
      </ChatContainer>
    </AppContainer>
  );
}

export default App;
