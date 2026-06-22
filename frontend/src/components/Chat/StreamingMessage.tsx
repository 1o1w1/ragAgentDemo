interface StreamingMessageProps {
  content: string;
  isComplete?: boolean;
}

export function StreamingMessage({ content, isComplete = false }: StreamingMessageProps) {
  return (
    <div style={{
      padding: '8px 16px',
      margin: '4px 0',
      backgroundColor: '#f3f4f6',
      borderRadius: '8px',
      maxWidth: '80%',
      alignSelf: 'flex-start'
    }}>
      <div style={{ whiteSpace: 'pre-wrap' }}>
        {content}
        {!isComplete && (
          <span style={{
            display: 'inline-block',
            width: '2px',
            height: '16px',
            backgroundColor: '#3b82f6',
            marginLeft: '2px',
            animation: 'blink 1s infinite'
          }} />
        )}
      </div>
      
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}