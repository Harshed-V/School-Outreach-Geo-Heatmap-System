export const getScoreColor = (score) => {
  if (score > 80) return "#d73027";
  if (score > 60) return "#fc8d59";
  if (score > 40) return "#fee08b";
  if (score > 20) return "#d9ef8b";
  return "#91cf60";
};
