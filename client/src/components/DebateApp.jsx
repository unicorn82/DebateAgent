import { useState, useEffect } from 'react';
import { 
  FaRobot, 
  FaGavel, 
  FaTrophy, 
  FaDownload,
  FaSpinner 
} from 'react-icons/fa';
import * as api from '../services/api';
import './DebateApp.css';

const DebateApp = () => {
  // State management
  const [topic, setTopic] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [numRounds, setNumRounds] = useState(3);
  
  const [affOptions, setAffOptions] = useState('');
  const [negOptions, setNegOptions] = useState('');
  
  const [rounds, setRounds] = useState({
    round1: { aff: '', neg: '' },
    round2: { aff: '', neg: '' },
    round3: { aff: '', neg: '' },
  });
  
  const [affFinal, setAffFinal] = useState('');
  const [negFinal, setNegFinal] = useState('');
  
  const [judgeResult, setJudgeResult] = useState(null);
  const [loading, setLoading] = useState({});
  const [statusMessage, setStatusMessage] = useState('');

  // Handle generate topics
  const handleGenerateTopics = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, topics: true });
    setStatusMessage('');
    
    try {
      const result = await api.generateTopics(topic);
      setAffOptions(result.affirmative_option);
      setNegOptions(result.negative_option);
      setStatusMessage('✅ Topics generated successfully!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, topics: false });
    }
  };

  // Handle generate affirmative option only
  const handleGenerateAffOption = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, affOption: true });
    try {
      console.log("topic", topic);
      const result = await api.generateAffirmativeOption(topic);
      console.log("result", result);
      setAffOptions(result.statement);
      setStatusMessage('✅ Affirmative option generated!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, affOption: false });
    }
  };

  // Handle generate negative option only
  const handleGenerateNegOption = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, negOption: true });
    try {
      const result = await api.generateNegativeOption(topic);
      setNegOptions(result.statement);
      setStatusMessage('✅ Negative option generated!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, negOption: false });
    }
  };

  // Collect all statements for a team
  const collectStatements = (team) => {
    const statements = [];
    Object.keys(rounds).forEach((roundKey, index) => {
      if (index < numRounds) {
        const statement = rounds[roundKey][team];
        if (statement && statement.trim()) {
          statements.push(statement);
        }
      }
    });
    return statements;
  };

  // Handle generate statement for a specific round
  const handleGenerateStatement = async (roundKey, team) => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    const loadingKey = `${roundKey}_${team}`;
    setLoading({ ...loading, [loadingKey]: true });
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affOptions,
        neg_options: negOptions,
        affirmative_statements: affStatements,
        negative_statements: negStatements,
        context: `Round ${roundKey.replace('round', '')} argument`
      };
      
      let result;
      if (team === 'aff') {
        result = await api.generateAffirmativeStatement(data);
      } else {
        result = await api.generateNegativeStatement(data);
      }
      
      setRounds({
        ...rounds,
        [roundKey]: {
          ...rounds[roundKey],
          [team]: result.statement
        }
      });
      
      setStatusMessage(`✅ ${team === 'aff' ? 'Affirmative' : 'Negative'} statement generated!`);
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, [loadingKey]: false });
    }
  };

  // Handle generate closing argument
  const handleGenerateClosing = async (team) => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    const loadingKey = `closing_${team}`;
    setLoading({ ...loading, [loadingKey]: true });
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affOptions,
        neg_options: negOptions,
        team_statements: team === 'aff' ? affStatements : negStatements,
        opponent_statements: team === 'aff' ? negStatements : affStatements
      };
      
      let result;
      if (team === 'aff') {
        result = await api.generateAffirmativeClosing(data);
      } else {
        result = await api.generateNegativeClosing(data);
      }
      
      if (team === 'aff') {
        setAffFinal(result.statement);
      } else {
        setNegFinal(result.statement);
      }
      
      setStatusMessage(`✅ ${team === 'aff' ? 'Affirmative' : 'Negative'} closing generated!`);
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, [loadingKey]: false });
    }
  };

  // Handle judge debate
  const handleJudge = async () => {
    if (!topic.trim()) {
      setStatusMessage('⚠️ Please enter a debate topic first.');
      return;
    }
    
    setLoading({ ...loading, judge: true });
    setStatusMessage('⚖️ Judging debate...');
    
    try {
      const affStatements = collectStatements('aff');
      const negStatements = collectStatements('neg');
      
      const data = {
        topic,
        aff_options: affOptions,
        neg_options: negOptions,
        affirmative_statements: affStatements,
        negative_statements: negStatements,
        aff_final: affFinal,
        neg_final: negFinal
      };
      
      const result = await api.judgeDebate(data);
      
      // Parse the result if it's a JSON string
      let parsedResult;
      try {
        let cleanResult = result.result;
        if (typeof cleanResult === 'string') {
          // Remove markdown code blocks if present
          cleanResult = cleanResult.replace(/```json/g, '').replace(/```/g, '').trim();
          parsedResult = JSON.parse(cleanResult);
        } else {
          parsedResult = result.result;
        }
      } catch (e) {
        console.error("Failed to parse judge result:", e);
        parsedResult = { result: result.result };
      }
      
      setJudgeResult(parsedResult);
      setStatusMessage('✅ Judging complete!');
    } catch (error) {
      setStatusMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, judge: false });
    }
  };

  // Download transcript
  const handleDownloadTranscript = () => {
    const affStatements = collectStatements('aff');
    const negStatements = collectStatements('neg');
    
    // Generate rounds content
    let roundsContent = '';
    const maxRounds = Math.max(affStatements.length, negStatements.length);
    
    for (let i = 0; i < maxRounds; i++) {
        roundsContent += `## Round ${i + 1}\n\n`;
        
        if (affStatements[i]) {
            roundsContent += `### Affirmative Argument\n${affStatements[i]}\n\n`;
        }
        
        if (negStatements[i]) {
            roundsContent += `### Negative Argument\n${negStatements[i]}\n\n`;
        }
    }

    const transcript = `# DEBATE TRANSCRIPT

**Topic:** ${topic}

## Affirmative Team Options
${affOptions}

## Negative Team Options
${negOptions}

${roundsContent}## Affirmative Final Summary
${affFinal}

## Negative Final Summary
${negFinal}

${judgeResult ? `## JUDGE DECISION
**Winner:** ${judgeResult.winner || 'N/A'}
**Affirmative Score:** ${judgeResult.affirmative_score || 'N/A'}
**Negative Score:** ${judgeResult.negative_score || 'N/A'}

**Reason:**
${judgeResult.reason || 'N/A'}` : ''}
`;

    const blob = new Blob([transcript], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debate_transcript_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="debate-app">
      <header className="app-header">
        <h1>🗣️ Debate App</h1>
        <p>Enter a topic, auto-generate team options, run multiple rounds, write final summaries, then have an AI judge pick a winner.</p>
      </header>

      {/* Configuration */}
      <div className="config-section">
        <div className="config-item">
          <label>Temperature: {temperature}</label>
          <input
            type="range"
            min="0"
            max="1.2"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
          />
        </div>
        <div className="config-item">
          <label>Number of Rounds:</label>
          <select value={numRounds} onChange={(e) => setNumRounds(parseInt(e.target.value))}>
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={3}>3</option>
          </select>
        </div>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div className="status-message">
          {statusMessage}
        </div>
      )}

      {/* Topic Input */}
      <div className="topic-section">
        <label>Debate Topic</label>
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., Should homework be banned in middle schools?"
          rows={3}
        />
      </div>

      {/* Generate Topics Button */}
      {/* <div className="action-section">
        <button 
          className="btn btn-primary"
          onClick={handleGenerateTopics}
          disabled={loading.topics}
        >
          {loading.topics ? <FaSpinner className="spin" /> : '✨'} Generate Team Options (AI)
        </button>
      </div> */}

      {/* Team Options */}
      <div className="team-options">
        <div className="team-column affirmative">
          <div className="team-header">
            <h2>✅ Affirmative Team</h2>
            <button 
              className="btn btn-sm"
              onClick={handleGenerateAffOption}
              disabled={loading.affOption}
            >
              {loading.affOption ? <FaSpinner className="spin" /> : <FaRobot />} AI Generate
            </button>
          </div>
          <textarea
            value={affOptions}
            onChange={(e) => setAffOptions(e.target.value)}
            placeholder="Affirmative team options (AI-generated, editable)"
            rows={8}
          />
        </div>

        <div className="team-column negative">
          <div className="team-header">
            <h2>❌ Negative Team</h2>
            <button 
              className="btn btn-sm"
              onClick={handleGenerateNegOption}
              disabled={loading.negOption}
            >
              {loading.negOption ? <FaSpinner className="spin" /> : <FaRobot />} AI Generate
            </button>
          </div>
          <textarea
            value={negOptions}
            onChange={(e) => setNegOptions(e.target.value)}
            placeholder="Negative team options (AI-generated, editable)"
            rows={8}
          />
        </div>
      </div>

      <hr />

      {/* Rounds */}
      {[1, 2, 3].map((roundNum) => {
        if (roundNum > numRounds) return null;
        const roundKey = `round${roundNum}`;
        
        return (
          <div key={roundKey} className="round-section">
            <h3>🔁 Round {roundNum}</h3>
            <div className="round-content">
              <div className="team-column affirmative">
                <div className="member-header">
                  <span>Affirmative Team</span>
                  <button 
                    className="btn btn-sm"
                    onClick={() => handleGenerateStatement(roundKey, 'aff')}
                    disabled={loading[`${roundKey}_aff`]}
                  >
                    {loading[`${roundKey}_aff`] ? <FaSpinner className="spin" /> : <FaRobot />} AI
                  </button>
                </div>
                <textarea
                  value={rounds[roundKey].aff}
                  onChange={(e) => setRounds({
                    ...rounds,
                    [roundKey]: { ...rounds[roundKey], aff: e.target.value }
                  })}
                  placeholder="Affirmative argument..."
                  rows={4}
                />
              </div>

              <div className="team-column negative">
                <div className="member-header">
                  <span>Negative Team</span>
                  <button 
                    className="btn btn-sm"
                    onClick={() => handleGenerateStatement(roundKey, 'neg')}
                    disabled={loading[`${roundKey}_neg`]}
                  >
                    {loading[`${roundKey}_neg`] ? <FaSpinner className="spin" /> : <FaRobot />} AI
                  </button>
                </div>
                <textarea
                  value={rounds[roundKey].neg}
                  onChange={(e) => setRounds({
                    ...rounds,
                    [roundKey]: { ...rounds[roundKey], neg: e.target.value }
                  })}
                  placeholder="Negative argument..."
                  rows={4}
                />
              </div>
            </div>
          </div>
        );
      })}

      <hr />

      {/* Final Summaries */}
      <div className="final-section">
        <h3>🧾 Final Team Summaries</h3>
        <div className="final-content">
          <div className="team-column affirmative">
            <div className="member-header">
              <span>Affirmative — Final Team Summary</span>
              <button 
                className="btn btn-sm"
                onClick={() => handleGenerateClosing('aff')}
                disabled={loading.closing_aff}
              >
                {loading.closing_aff ? <FaSpinner className="spin" /> : <FaRobot />} AI
              </button>
            </div>
            <textarea
              value={affFinal}
              onChange={(e) => setAffFinal(e.target.value)}
              placeholder="Affirmative final summary..."
              rows={5}
            />
          </div>

          <div className="team-column negative">
            <div className="member-header">
              <span>Negative — Final Team Summary</span>
              <button 
                className="btn btn-sm"
                onClick={() => handleGenerateClosing('neg')}
                disabled={loading.closing_neg}
              >
                {loading.closing_neg ? <FaSpinner className="spin" /> : <FaRobot />} AI
              </button>
            </div>
            <textarea
              value={negFinal}
              onChange={(e) => setNegFinal(e.target.value)}
              placeholder="Negative final summary..."
              rows={5}
            />
          </div>
        </div>
      </div>

      <hr />

      {/* Judge Button */}
      <div className="action-section">
        <button 
          className="btn btn-primary btn-large"
          onClick={handleJudge}
          disabled={loading.judge}
        >
          {loading.judge ? <FaSpinner className="spin" /> : <FaGavel />} Judge Winner (AI)
        </button>
      </div>

      {/* Judge Results */}
      {judgeResult && (
        <div className="judge-results">
          <h3>🏆 Judge Results</h3>
          
          <div className="winner-display">
            <FaTrophy className="trophy-icon" />
            <h2>{judgeResult.winner?.toUpperCase() || 'UNKNOWN'} TEAM WINS! 🎉</h2>
          </div>

          <div className="scores-section">
            <div className="score-box affirmative">
              <h4>✅ Affirmative Score</h4>
              <div className="score">{judgeResult.affirmative_score || 'N/A'}/25</div>
            </div>
            <div className="score-box negative">
              <h4>❌ Negative Score</h4>
              <div className="score">{judgeResult.negative_score || 'N/A'}/25</div>
            </div>
          </div>

          <div className="reasoning-section">
            <h4>📝 Judge's Reasoning</h4>
            <p>{judgeResult.reason || 'No reasoning provided'}</p>
          </div>

          <div className="action-section">
            <button 
              className="btn btn-secondary"
              onClick={handleDownloadTranscript}
            >
              <FaDownload /> Download Transcript
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DebateApp;
