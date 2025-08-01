// Automated Field Validation Tests for Job Application Form
// This script can be adapted for Cypress, Playwright, or Selenium

describe('Job Application Form - Field Validation', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3001/apply/{property_id}');
  });

  describe('Personal Information Fields', () => {
    it('should validate first name field', () => {
      // Test empty value
      cy.get('[name="firstName"]').clear().blur();
      cy.contains('First name is required').should('be.visible');
      
      // Test special characters
      cy.get('[name="firstName"]').type('<script>alert("xss")</script>');
      cy.get('[name="firstName"]').should('not.contain', '<script>');
    });
    
    it('should validate email field', () => {
      // Test invalid email
      cy.get('[name="email"]').type('invalid.email');
      cy.contains('Invalid email format').should('be.visible');
    });
  });
});