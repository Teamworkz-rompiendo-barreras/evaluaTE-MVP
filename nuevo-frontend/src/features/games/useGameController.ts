// nuevo-frontend/src/features/games/useGameController.ts

import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { markGameComplete } from '../progress/progressSlice';
import { UserDecision } from '@/types/skills';
import { SceneOption } from '@/types/game-scene';
import { useGetSceneQuery } from "./scenesApi";

interface UseGameControllerProps {
  sceneId: number;
}

const useGameController = ({ sceneId }: UseGameControllerProps) => {
  const dispatch = useDispatch();
  const { data: scene } = useGetSceneQuery(String(sceneId));

  const [currentStep, setCurrentStep] = useState(0);
  const [timeLeft, setTimeLeft] = useState(scene?.steps?.[currentStep]?.timeLimit || 0);
  const [choices, setChoices] = useState<UserDecision[]>([]);
  const [completed, setCompleted] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (scene && scene.steps && scene.steps[currentStep]) {
      setTimeLeft(scene.steps[currentStep].timeLimit || 0);
    }
  }, [scene, currentStep]);

  useEffect(() => {
    if (scene && scene.steps && currentStep >= scene.steps.length) {
      setCompleted(true);
      dispatch(markGameComplete(String(sceneId)));
    }
  }, [scene, currentStep, dispatch, sceneId]);

  useEffect(() => {
    if (scene && scene.steps) {
      const totalSteps = scene.steps.length;
      setProgress((currentStep / totalSteps) * 100);
    }
  }, [scene, currentStep]);

  useEffect(() => {
    if (scene && scene.steps) {
      const timer = setInterval(() => {
        setTimeLeft((prevTime: number) => {
          if (prevTime > 0) {
            return prevTime - 1;
          } else {
            clearInterval(timer);
            return 0;
          }
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [scene, currentStep]);

  const nextStep = () => {
    if (scene && scene.steps && currentStep < scene.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const makeChoice = (option: SceneOption) => {
    const decision: UserDecision = {
      sceneId,
      stepIndex: currentStep,
      optionText: option.text,
      isCorrect: option.isCorrect || false,
      skillImpacts: option.skillImpact || {},
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      screenResolution: `${window.innerWidth}x${window.innerHeight}`,
    };
    setChoices([...choices, decision]);
  };

  const resetGame = () => {
    setCurrentStep(0);
    setTimeLeft(scene?.steps?.[0]?.timeLimit || 0);
    setChoices([]);
    setCompleted(false);
    setProgress(0);
  };

  const getSkillScores = () => {
    const scores: Record<string, number> = {};
    choices.forEach((choice) => {
      Object.keys(choice.skillImpacts).forEach((skill) => {
        if (!scores[skill]) {
          scores[skill] = 0;
        }
        scores[skill] += choice.skillImpacts[skill];
      });
    });
    return scores;
  };

  return {
    currentStep,
    timeLeft,
    choices,
    completed,
    nextStep,
    prevStep,
    makeChoice,
    resetGame,
    progress,
    getSkillScores, // Agregado getSkillScores
  };
};

export default useGameController;