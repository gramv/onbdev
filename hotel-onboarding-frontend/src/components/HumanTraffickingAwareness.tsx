import React, { useState } from 'react';
import { AlertTriangle, Phone, Shield, Users, CheckCircle } from 'lucide-react';

interface HumanTraffickingAwarenessProps {
  onComplete: (data: any) => void;
  language?: 'en' | 'es';
}

const HumanTraffickingAwareness: React.FC<HumanTraffickingAwarenessProps> = ({
  onComplete,
  language = 'en'
}) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [hasCompletedTraining, setHasCompletedTraining] = useState(false);

  const content = {
    en: {
      title: "Human Trafficking Awareness Training",
      subtitle: "Required Federal Training - Complete All Sections",
      sections: [
        {
          title: "What is Human Trafficking?",
          icon: <Users className="w-8 h-8 text-red-500" />,
          content: [
            "Human trafficking is a form of modern-day slavery that involves the use of force, fraud, or coercion to obtain some type of labor or commercial sex act.",
            "It affects millions of people worldwide, including in the United States.",
            "Victims can be any age, race, gender, or nationality.",
            "Trafficking can happen in any community - urban, suburban, or rural."
          ]
        },
        {
          title: "Types of Human Trafficking",
          icon: <AlertTriangle className="w-8 h-8 text-orange-500" />,
          content: [
            "Sex Trafficking: The recruitment, harboring, transportation, provision, obtaining, patronizing, or soliciting of a person for commercial sex acts through force, fraud, or coercion.",
            "Labor Trafficking: The recruitment, harboring, transportation, provision, or obtaining of a person for labor or services through force, fraud, or coercion.",
            "Common industries include: restaurants, hotels, domestic work, agriculture, manufacturing, and construction."
          ]
        },
        {
          title: "Warning Signs in the Workplace",
          icon: <Shield className="w-8 h-8 text-blue-500" />,
          content: [
            "Employee appears malnourished, injured, or shows signs of abuse",
            "Employee is not allowed to speak for themselves or is always accompanied",
            "Employee works excessive hours and has few or no days off",
            "Employee lives at the workplace or in overcrowded conditions",
            "Employee owes large debt and is unable to leave until debt is paid",
            "Employee's identification documents are held by someone else",
            "Employee appears fearful, anxious, or submissive"
          ]
        },
        {
          title: "How to Report Suspected Trafficking",
          icon: <Phone className="w-8 h-8 text-green-500" />,
          content: [
            "National Human Trafficking Hotline: 1-888-373-7888",
            "Text: 233733 (BEFREE)",
            "Online: humantraffickinghotline.org",
            "Local Law Enforcement: 911 (in emergencies)",
            "All reports can be made anonymously",
            "Available 24/7 in multiple languages"
          ]
        }
      ],
      quiz: {
        title: "Knowledge Check",
        questions: [
          {
            question: "Human trafficking only involves sex trafficking.",
            correct: false,
            explanation: "Human trafficking includes both sex trafficking and labor trafficking."
          },
          {
            question: "Victims of human trafficking can be any age, race, or gender.",
            correct: true,
            explanation: "Correct. Human trafficking affects people of all backgrounds."
          },
          {
            question: "If I suspect human trafficking, I should confront the suspected trafficker directly.",
            correct: false,
            explanation: "Never confront suspected traffickers. Call the National Hotline: 1-888-373-7888"
          },
          {
            question: "The National Human Trafficking Hotline is available 24/7.",
            correct: true,
            explanation: "Correct. The hotline is available 24 hours a day, 7 days a week."
          }
        ]
      },
      acknowledgment: {
        title: "Training Acknowledgment",
        statements: [
          "I have completed the required Human Trafficking Awareness Training",
          "I understand how to identify potential signs of human trafficking",
          "I know how to report suspected human trafficking incidents",
          "I understand this training is required by federal law"
        ]
      }
    },
    es: {
      title: "Capacitación sobre Concientización del Tráfico Humano",
      subtitle: "Capacitación Federal Requerida - Complete Todas las Secciones",
      sections: [
        {
          title: "¿Qué es el Tráfico Humano?",
          icon: <Users className="w-8 h-8 text-red-500" />,
          content: [
            "El tráfico humano es una forma de esclavitud moderna que implica el uso de fuerza, fraude o coacción para obtener algún tipo de trabajo o acto sexual comercial.",
            "Afecta a millones de personas en todo el mundo, incluso en los Estados Unidos.",
            "Las víctimas pueden ser de cualquier edad, raza, género o nacionalidad.",
            "El tráfico puede ocurrir en cualquier comunidad: urbana, suburbana o rural."
          ]
        }
      ],
      quiz: {
        title: "Verificación de Conocimiento",
        questions: [
          {
            question: "El tráfico humano solo involucra tráfico sexual.",
            correct: false,
            explanation: "El tráfico humano incluye tanto tráfico sexual como tráfico laboral."
          },
          {
            question: "Las víctimas del tráfico humano pueden ser de cualquier edad, raza o género.",
            correct: true,
            explanation: "Correcto. El tráfico humano afecta a personas de todos los orígenes."
          },
          {
            question: "Si sospecho tráfico humano, debo confrontar directamente al presunto traficante.",
            correct: false,
            explanation: "Nunca confronte a presuntos traficantes. Llame a la Línea Nacional: 1-888-373-7888"
          },
          {
            question: "La Línea Nacional de Tráfico Humano está disponible 24/7.",
            correct: true,
            explanation: "Correcto. La línea está disponible las 24 horas del día, los 7 días de la semana."
          }
        ]
      },
      acknowledgment: {
        title: "Reconocimiento de Capacitación",
        statements: [
          "He completado la Capacitación de Concientización sobre Tráfico Humano requerida",
          "Entiendo cómo identificar posibles signos de tráfico humano",
          "Sé cómo reportar incidentes sospechosos de tráfico humano",
          "Entiendo que esta capacitación es requerida por ley federal"
        ]
      }
    }
  };

  const currentContent = content[language];
  const sections = currentContent.sections;

  const handleQuizResponse = (questionIndex: number, answer: boolean) => {
    setResponses({
      ...responses,
      [`quiz_${questionIndex}`]: answer
    });
  };

  const handleNext = () => {
    if (currentSection < sections.length - 1) {
      setCurrentSection(currentSection + 1);
    } else if (currentSection === sections.length - 1) {
      // Show quiz
      setCurrentSection(sections.length);
    } else if (currentSection === sections.length) {
      // Show acknowledgment
      setCurrentSection(sections.length + 1);
    }
  };

  const handleComplete = () => {
    const completionData = {
      completed_at: new Date().toISOString(),
      language: language,
      quiz_responses: responses,
      training_duration_minutes: 15, // Estimate
      ip_address: '', // Would be captured on backend
      user_agent: navigator.userAgent
    };
    
    setHasCompletedTraining(true);
    onComplete(completionData);
  };

  const renderSection = (section: any, index: number) => (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center gap-4 mb-6">
        {section.icon}
        <h2 className="text-2xl font-bold text-gray-800">{section.title}</h2>
      </div>
      
      <div className="space-y-4">
        {section.content.map((paragraph: string, idx: number) => (
          <p key={idx} className="text-gray-700 leading-relaxed text-lg">
            {paragraph}
          </p>
        ))}
      </div>
      
      <div className="flex justify-between items-center mt-8">
        <div className="text-sm text-gray-500">
          Section {index + 1} of {sections.length}
        </div>
        <button
          onClick={handleNext}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  );

  const renderQuiz = () => (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">{currentContent.quiz.title}</h2>
      
      <div className="space-y-6">
        {currentContent.quiz.questions.map((q: any, index: number) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <p className="font-medium text-gray-800 mb-4">{q.question}</p>
            
            <div className="flex gap-4 mb-3">
              <button
                onClick={() => handleQuizResponse(index, true)}
                className={`px-4 py-2 rounded ${
                  responses[`quiz_${index}`] === true
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                True
              </button>
              <button
                onClick={() => handleQuizResponse(index, false)}
                className={`px-4 py-2 rounded ${
                  responses[`quiz_${index}`] === false
                    ? 'bg-red-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                False
              </button>
            </div>
            
            {responses[`quiz_${index}`] !== undefined && (
              <div className={`p-3 rounded ${
                responses[`quiz_${index}`] === q.correct
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {responses[`quiz_${index}`] === q.correct ? '✓ Correct!' : '✗ Incorrect.'} {q.explanation}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="flex justify-between items-center mt-8">
        <div className="text-sm text-gray-500">
          Knowledge Check
        </div>
        <button
          onClick={handleNext}
          disabled={currentContent.quiz.questions.some((_, index) => responses[`quiz_${index}`] === undefined)}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Continue to Acknowledgment
        </button>
      </div>
    </div>
  );

  const renderAcknowledgment = () => (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">{currentContent.acknowledgment.title}</h2>
      
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-yellow-600 mt-1" />
          <div>
            <h3 className="font-semibold text-yellow-800 mb-2">Important Legal Requirement</h3>
            <p className="text-yellow-700">
              This training is required by federal law. Your completion will be recorded and may be audited by regulatory authorities.
            </p>
          </div>
        </div>
      </div>
      
      <div className="space-y-4 mb-8">
        {currentContent.acknowledgment.statements.map((statement: string, index: number) => (
          <div key={index} className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 mt-1" />
            <span className="text-gray-700">{statement}</span>
          </div>
        ))}
      </div>
      
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h3 className="font-semibold text-gray-800 mb-3">Emergency Contact Information</h3>
        <div className="space-y-2">
          <p><strong>National Human Trafficking Hotline:</strong> 1-888-373-7888</p>
          <p><strong>Text:</strong> 233733 (BEFREE)</p>
          <p><strong>Website:</strong> humantraffickinghotline.org</p>
          <p><strong>Emergency:</strong> 911</p>
        </div>
      </div>
      
      {!hasCompletedTraining ? (
        <button
          onClick={handleComplete}
          className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-semibold"
        >
          I Acknowledge Completion of This Training
        </button>
      ) : (
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-green-800 mb-2">Training Completed Successfully</h3>
          <p className="text-gray-600">Your completion has been recorded.</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto p-6">
          <h1 className="text-3xl font-bold text-gray-800">{currentContent.title}</h1>
          <p className="text-gray-600 mt-2">{currentContent.subtitle}</p>
          
          {/* Progress bar */}
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-500 mb-2">
              <span>Progress</span>
              <span>{Math.round(((currentSection + 1) / (sections.length + 2)) * 100)}% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentSection + 1) / (sections.length + 2)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
      
      <div className="py-8">
        {currentSection < sections.length && renderSection(sections[currentSection], currentSection)}
        {currentSection === sections.length && renderQuiz()}
        {currentSection === sections.length + 1 && renderAcknowledgment()}
      </div>
    </div>
  );
};

export default HumanTraffickingAwareness;