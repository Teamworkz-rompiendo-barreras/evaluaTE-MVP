// Componente para mostrar estrellas del CV

interface StarsProps {
  value: number;
  maxValue?: number;
  className?: string;
}

export function Stars({ value, maxValue = 5, className = "" }: StarsProps) {
  const full = "★".repeat(Math.max(0, Math.min(maxValue, value)));
  const empty = "☆".repeat(maxValue - full.length);
  
  return (
    <span 
      className={className}
      aria-label={`${value} de ${maxValue}`}
      title={`${value} de ${maxValue} estrellas`}
    >
      {full}{empty}
    </span>
  );
}

export default Stars;
