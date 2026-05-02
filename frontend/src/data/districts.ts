export type District = {
  id: string;
  name: string;
  score: number;
  schools: number;
  highSecondaryCount?: number;
  lat: number;
  lng: number;
  priority: "high" | "medium" | "low";
};

export const DISTRICTS: District[] = [
  {
    id: "chennai",
    name: "Chennai",
    score: 360,
    schools: 120,
    highSecondaryCount: 45,
    lat: 13.0827,
    lng: 80.2707,
    priority: "high",
  },
  {
    id: "coimbatore",
    name: "Coimbatore",
    score: 245,
    schools: 85,
    highSecondaryCount: 28,
    lat: 11.0081,
    lng: 76.9954,
    priority: "high",
  },
  {
    id: "madurai",
    name: "Madurai",
    score: 165,
    schools: 65,
    highSecondaryCount: 18,
    lat: 9.9252,
    lng: 78.1198,
    priority: "medium",
  },
  {
    id: "salem",
    name: "Salem",
    score: 140,
    schools: 52,
    highSecondaryCount: 15,
    lat: 11.6643,
    lng: 78.1460,
    priority: "medium",
  },
  {
    id: "tiruchirappalli",
    name: "Tiruchirappalli",
    score: 130,
    schools: 48,
    highSecondaryCount: 14,
    lat: 10.7905,
    lng: 78.7047,
    priority: "medium",
  },
];
