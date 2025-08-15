import React from 'react';

// Test component to verify React is working properly
export const TestReact = () => {
  const [count, setCount] = React.useState(0);
  
  React.useEffect(() => {
    console.log('✅ React hooks are working properly!');
    console.log('React version:', React.version);
  }, []);

  return (
    <div>
      <h1>React Test Component</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};

// Verify React singleton
if (typeof window !== 'undefined') {
  (window as any).__REACT_TEST__ = React;
  console.log('React instance stored for verification');
}