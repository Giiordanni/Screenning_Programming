document.addEventListener('DOMContentLoaded', async function() {
    const tokenParam = new URLSearchParams(window.location.search).get('token');
    const token = localStorage.getItem('token') || tokenParam;

    if (!token) {
        // Sem token, redireciona para a tela de login
        window.location.href = '../html/login.html';
        return;
    }

    checagemToken(token);

    try {
        // Decodifica o token JWT
        const decode = jwt_decode(token);
        const groupId = decode.groupId;

        // Verificar convite
        const inviteResponse = await fetch('https://projetodepesquisa.vercel.app/api/verifyInvite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const inviteData = await inviteResponse.json();

        if (!inviteResponse.ok) {
            throw new Error(inviteData.error);
        }

        // Atualizar o grupo do aluno
        const response = await fetch(`https://projetodepesquisa.vercel.app/api/group/student/${groupId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message);
        }

        // Redireciona para a página de grupos após adicionar ao grupo
        setTimeout(() => {
            window.location.href = '../html/grupos-alunos.html';
        }, 1000);

    } catch (error) {
        console.error('Erro ao carregar grupos ou verificar convite:', error);
        // Em caso de erro, redireciona para a tela de login
        setTimeout(() => {
            window.location.href = '../html/login.html';
        }, 1000);
    }
});

function checagemToken(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const tempo = Date.now() / 1000;

        if (payload.exp && payload.exp > tempo) {
            // Token válido, segue o fluxo normal
            return;
        } else {
            // Token expirado, remove e redireciona para o login
            localStorage.removeItem('token');
            setTimeout(() => {
                window.location.href = '../html/login.html';
            }, 1000);
        }
    } catch (e) {
        // Token inválido, remove e redireciona para o login
        localStorage.removeItem('token');
        setTimeout(() => {
            window.location.href = '../html/login.html';
        }, 1000);
    }
}
