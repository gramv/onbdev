import React from 'react';
import HumanTraffickingAwareness from './components/HumanTraffickingAwareness';
import WeaponsPolicyAcknowledgment from './components/WeaponsPolicyAcknowledgment';
import I9Section1Form from './components/I9Section1Form';

const TestComponents: React.FC = () => {
  const [currentComponent, setCurrentComponent] = React.useState<string>('human-trafficking');

  const handleComplete = (data: any) => {
    console.log('Component completed with data:', data);
    alert('Component completed! Check console for data.');
  };

  const renderComponent = () => {
    switch (currentComponent) {
      case 'human-trafficking':
        return (
          <HumanTraffickingAwareness 
            onComplete={handleComplete}
            language="en"
          />
        );
      case 'weapons-policy':
        return (
          <WeaponsPolicyAcknowledgment 
            onComplete={handleComplete}
            language="en"
          />
        );
      case 'i9-section1':
        return (
          <I9Section1Form 
            onComplete={handleComplete}
            language="en"
          />
        );
      default:
        return <div>Select a component to test</div>;
    }
  };

  return (
    <div>
      {/* Component Selector */}
      <div className="fixed top-4 right-4 z-50 bg-white border border-gray-300 rounded-lg p-4 shadow-lg">
        <h3 className="font-bold mb-3">Test Components</h3>
        <div className="space-y-2">
          <button
            onClick={() => setCurrentComponent('human-trafficking')}
            className={`block w-full text-left px-3 py-2 rounded ${
              currentComponent === 'human-trafficking' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            Human Trafficking
          </button>
          <button
            onClick={() => setCurrentComponent('weapons-policy')}
            className={`block w-full text-left px-3 py-2 rounded ${
              currentComponent === 'weapons-policy' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            Weapons Policy
          </button>
          <button
            onClick={() => setCurrentComponent('i9-section1')}
            className={`block w-full text-left px-3 py-2 rounded ${
              currentComponent === 'i9-section1' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            I-9 Section 1
          </button>
        </div>
      </div>

      {/* Component Display */}
      {renderComponent()}
    </div>
  );
};

export default TestComponents;