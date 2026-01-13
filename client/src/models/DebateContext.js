/**
 * POJO for Team Context
 */
export class TeamContext {
  constructor(role, providerId, temperature = 0.7) {
    this.role = role;
    this.providerId = providerId;
    this.temperature = temperature;
    this.options = '';
    this.statements = ['', '', '']; // Initialize with 3 empty rounds by default
    this.finalSummary = '';
  }
}

/**
 * POJO for Judge Context
 */
export class JudgeContext {
  constructor(providerId, temperature = 0.7) {
    this.role = 'judge';
    this.providerId = providerId;
    this.temperature = temperature;
    this.result = null; // Stores the parsed judge result object
  }
}
