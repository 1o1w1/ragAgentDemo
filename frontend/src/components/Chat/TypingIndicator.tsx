export function TypingIndicator() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '8px 16px',
      color: '#6b7280',
      fontSize: 14
    }}>
      <div style={{
        display: 'flex',
        gap: '4px',
        marginRight: '8px'
      }}>
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out'
        }} />
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out 0.2s'
        }} />
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out 0.4s'
        }} />
      </div>
      <span>正在输入...</span>
      
      <style>{`
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          30% {
            transform: translateY(-4px);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
