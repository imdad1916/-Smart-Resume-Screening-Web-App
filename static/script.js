document.getElementById('resumeForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById('resume');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('resume', file);

  const loader = document.getElementById('loader');
  const resultDiv = document.getElementById('result');
  const toast = document.getElementById('toast');

  loader.style.display = 'block';
  resultDiv.innerHTML = '';

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    loader.style.display = 'none';

    if (data && data.extracted_data) {

      const { Name, Email, Skills, Experience } = data.extracted_data;

      resultDiv.innerHTML = `
        <h3>${data.message}</h3>
        <p><strong>Name:</strong> ${Name || 'N/A'}</p>
        <p><strong>Email:</strong> ${Email || 'N/A'}</p>
        <p><strong>Skills:</strong> ${Skills || 'N/A'}</p>
        <p><strong>Experience:</strong> ${Experience || 'N/A'}</p>
        <div class="match-bar">
          <div class="match-bar-fill" id="matchBarFill">0%</div>
        </div>
      `;

      const keywords = ['MongoDB', 'Express', 'React', 'Node.js', 'Python', 'Java'];
      let matchCount = 0;
      keywords.forEach(keyword => {
        if ((Skills || '').toLowerCase().includes(keyword.toLowerCase())) {
          matchCount++;
        }
      });

      const matchPercentage = Math.floor((matchCount / keywords.length) * 100);
      const matchBar = document.getElementById('matchBarFill');
      matchBar.style.width = `${matchPercentage}%`;
      matchBar.innerText = `${matchPercentage}% Match`;

      // Change bar color based on percentage
      if (matchPercentage >= 70) {
        matchBar.style.backgroundColor = '#4CAF50'; // green
      } else if (matchPercentage >= 40) {
        matchBar.style.backgroundColor = '#FFA500'; // orange
      } else {
        matchBar.style.backgroundColor = '#f44336'; // red
      }
    } else {
      showToast('No data extracted.', 'error');
      resultDiv.innerHTML = '<p>No text extracted.</p>';
    }
  } catch (error) {
    loader.style.display = 'none';
    showToast('Upload failed. Please try again.', 'error');
    console.error('Upload failed:', error);
  }
});

function showToast(message, type) {
  const toast = document.getElementById('toast');
  toast.innerText = message;
  toast.className = `toast toast-${type}`;
  toast.style.display = 'block';

  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

document.getElementById('loadRankingBtn').addEventListener('click', async function () {
  const section = document.getElementById('rankingSection');
  section.innerHTML = 'Loading ranked resumes...';

  try {
    const res = await fetch('/ranked-resumes');
    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      section.innerHTML = '<p>No resumes found.</p>';
      return;
    }

    section.innerHTML = '';
    data.forEach((resume, index) => {
      const card = document.createElement('div');
      card.style.border = '1px solid #ccc';
      card.style.padding = '10px';
      card.style.margin = '10px 0';
      card.style.backgroundColor = '#f9f9f9';

      let color = '#f44336'; // red
      if (resume.match >= 70) color = '#4CAF50'; // green
      else if (resume.match >= 40) color = '#FFA500'; // orange

      card.innerHTML = `
        <h3>#${index + 1} - ${resume.name}</h3>
        <p><strong>Email:</strong> ${resume.email}</p>
        <p><strong>Skills:</strong> ${resume.skills}</p>
        <p><strong>Experience:</strong> ${resume.experience}</p>
        <p><strong>Match:</strong> <span style="color:${color}">${resume.match}%</span></p>
        <a href="${resume.url}" target="_blank">🔗 View Resume</a>
      `;

      section.appendChild(card);
    });
  } catch (err) {
    console.error(err);
    section.innerHTML = '<p style="color:red;">Error loading rankings.</p>';
  }
});
