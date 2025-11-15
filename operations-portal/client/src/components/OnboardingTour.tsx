import { useState, useEffect } from "react";
import Joyride, { CallBackProps, STATUS, Step } from "react-joyride";

interface OnboardingTourProps {
  run: boolean;
  onFinish: () => void;
}

export function OnboardingTour({ run, onFinish }: OnboardingTourProps) {
  const [stepIndex, setStepIndex] = useState(0);

  const steps: Step[] = [
    {
      target: "body",
      content: (
        <div>
          <h2 className="text-xl font-bold mb-2">Welcome to UltraCore Operations Portal! 🎉</h2>
          <p>
            Let's take a quick tour to help you get started with managing portfolios, monitoring RL agents,
            and accessing real-time market data. This tour will take about 2 minutes.
          </p>
        </div>
      ),
      placement: "center",
      disableBeacon: true,
    },
    {
      target: '[data-tour="kpi-cards"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Key Performance Indicators</h3>
          <p>
            Monitor critical metrics at a glance: Total AUM (Assets Under Management), active portfolios,
            loans, and system health. Hover over the info icons for detailed explanations.
          </p>
        </div>
      ),
      placement: "bottom",
    },
    {
      target: '[data-tour="modules"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Portal Modules</h3>
          <p>
            Access all major features through these module cards. Each module provides specialized
            functionality for different aspects of UltraCore operations.
          </p>
        </div>
      ),
      placement: "top",
    },
    {
      target: '[data-tour="portfolios-module"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Portfolios</h3>
          <p>
            Manage investment portfolios and holdings. View performance metrics, asset allocations,
            and track returns across all managed accounts.
          </p>
        </div>
      ),
      placement: "right",
    },
    {
      target: '[data-tour="securities-module"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Global Securities Register</h3>
          <p>
            Access the comprehensive securities database covering equities, crypto, and alternative assets.
            Real-time prices are enriched from Fiscal.ai and Yahoo Finance APIs.
          </p>
        </div>
      ),
      placement: "right",
    },
    {
      target: '[data-tour="kafka-module"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Kafka Events</h3>
          <p>
            Monitor real-time event streams for market data updates. All price changes are published
            to Kafka for ML/RL agent consumption and backtesting.
          </p>
        </div>
      ),
      placement: "right",
    },
    {
      target: '[data-tour="rl-agents-module"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">RL Agents</h3>
          <p>
            Track reinforcement learning agent training progress, view reward curves, and monitor
            portfolio performance across Alpha, Beta, Gamma, Delta, and Epsilon agents.
          </p>
        </div>
      ),
      placement: "right",
    },
    {
      target: '[data-tour="sidebar"]',
      content: (
        <div>
          <h3 className="font-semibold mb-2">Navigation Sidebar</h3>
          <p>
            Use the sidebar to quickly navigate between modules. Your current location is highlighted,
            and you can collapse the sidebar for more screen space.
          </p>
        </div>
      ),
      placement: "right",
    },
    {
      target: "body",
      content: (
        <div>
          <h2 className="text-xl font-bold mb-2">You're All Set! ✅</h2>
          <p className="mb-3">
            You now know the basics of the UltraCore Operations Portal. Explore each module to discover
            more features, or restart this tour anytime from the Dashboard.
          </p>
          <p className="text-sm text-muted-foreground">
            💡 Tip: Hover over metrics with info icons for detailed explanations.
          </p>
        </div>
      ),
      placement: "center",
    },
  ];

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status, index, action } = data;

    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status as any)) {
      onFinish();
      setStepIndex(0);
    } else if (action === "next" || action === "prev") {
      setStepIndex(index + (action === "next" ? 1 : -1));
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      stepIndex={stepIndex}
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: "#2563eb",
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: 8,
          padding: 20,
        },
        tooltipContent: {
          padding: "10px 0",
        },
        buttonNext: {
          backgroundColor: "#2563eb",
          borderRadius: 6,
          padding: "8px 16px",
        },
        buttonBack: {
          color: "#64748b",
          marginRight: 10,
        },
        buttonSkip: {
          color: "#64748b",
        },
      }}
      locale={{
        back: "Back",
        close: "Close",
        last: "Finish",
        next: "Next",
        skip: "Skip Tour",
      }}
    />
  );
}
