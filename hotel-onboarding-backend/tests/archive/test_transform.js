// Simulating the backend response
const backendResponse = [
  {
    id: "959a01a6-6bb1-4bbb-a779-acaff92518f4",
    email: "gouthi321@123.com",
    first_name: "Goutham",
    last_name: "vemula",
    properties: [
      {
        id: "b1d60a13-ba0d-45bd-b709-87076abc64dc",
        name: "Grand Plaza Hotel",
        city: "Downtown",
        state: "CA"
      }
    ]
  }
];

// The fixed transform logic
const transformedManagers = backendResponse.map((manager) => ({
  id: manager.id,
  email: manager.email,
  first_name: manager.first_name,
  last_name: manager.last_name,
  property_id: manager.properties && manager.properties[0] ? manager.properties[0].id : null,
  property_name: manager.properties && manager.properties[0] ? manager.properties[0].name : null,
  is_active: manager.is_active \!== undefined ? manager.is_active : true,
  created_at: manager.created_at
}));

console.log("Transformed manager:");
console.log(JSON.stringify(transformedManagers[0], null, 2));
console.log("\nProperty assignment check:");
console.log("Property ID:", transformedManagers[0].property_id ? "✓ Found" : "✗ Missing");
console.log("Property Name:", transformedManagers[0].property_name ? `✓ ${transformedManagers[0].property_name}` : "✗ Missing");
