export const MapLegend = () => {
  return (
    <div className="map-legend">
      <h4>Score bands</h4>
      <p><span className="dot score-very-high" /> Very high (81-100)</p>
      <p><span className="dot score-high" /> High (61-80)</p>
      <p><span className="dot score-mid" /> Medium (41-60)</p>
      <p><span className="dot score-low" /> Low (21-40)</p>
      <p><span className="dot score-very-low" /> Very low (0-20)</p>
    </div>
  );
};
