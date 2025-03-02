# -*- coding: utf-8 -*-

from flask import Flask,flash, render_template, request, redirect, url_for, session, json, abort
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['JSON_AS_ASCII'] = False

# Cargar participantes
def load_participants():
    with open('participantes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_participants(participants):
    with open('participantes.json', 'w', encoding='utf-8') as f:
        json.dump(participants, f, ensure_ascii=False, indent=4)

# Cargar candidatos desde JSON
def load_candidates():
    with open('candidatos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_candidates(candidates):
    with open('candidatos.json', 'w', encoding='utf-8' ) as f:
        json.dump(candidates, f, ensure_ascii=False)

# Modificar la ruta principal
@app.route('/')
def home():
    return redirect(url_for('login'))

# Nueva ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = int(request.form['code'])
        participants = load_participants()
        
        for participant in participants:
            if participant['code'] == code:
                if not participant['voted']:
                    session['user_code'] = code
                    session['user_name'] = participant['name']
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error="Ya has votado anteriormente")
        return render_template('login.html', error="Código inválido")
    return render_template('login.html')


# Modificar la ruta index
@app.route('/index')
def index():
    if 'user_code' not in session:
        return redirect(url_for('login'))
    
    participants = load_participants()
    for participant in participants:
        if participant['code'] == session['user_code'] and participant['voted']:
            return redirect(url_for('login'))
    
    candidates = load_candidates()
    return render_template('index.html', candidates=candidates, nombrepart=session['user_name'])

# Modificar la ruta de votación
@app.route('/vote/<int:candidate_id>', methods=['POST'])
def vote(candidate_id):
    if 'user_code' not in session:
        return redirect(url_for('login'))
    
    participants = load_participants()
    for participant in participants:
        if participant['code'] == session['user_code']:
            if participant['voted']:
                return redirect(url_for('login'))
            
            # Actualizar participantes
            participant['voted'] = True
            save_participants(participants)
            
            # Actualizar candidatos
            candidates = load_candidates()
            for candidate in candidates:
                if candidate['id'] == candidate_id:
                    candidate['votes'] += 1
            save_candidates(candidates)
            
            session.pop('user_code', None)
            flash('¡ Gracias por tu voto !')
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/results')
def results():
    candidates = load_candidates()
    # Ordenar por votos descendentes
    sorted_candidates = sorted(candidates, key=lambda x: x['votes'], reverse=True)
    
    # Asignar cargos
    positions = ['Presidente', 'Vicepresidente', 'Secretario', 'Tesorero']
    for i, candidate in enumerate(sorted_candidates[:4]):
        candidate['position'] = positions[i] if i < len(positions) else 'Miembro'
    
    return render_template('results.html', candidates=sorted_candidates)

# Nueva ruta de logout
@app.route('/logout')
def logout():
    session.pop('user_code', None)
    return redirect(url_for('login'))

@app.route('/reset', methods=['POST'])
def reset():
    # Resetear candidatos
    candidates = load_candidates()
    for candidate in candidates:
        candidate['votes'] = 0
    save_candidates(candidates)
    
    # Resetear participantes
    participants = load_participants()
    for participant in participants:
        participant['voted'] = False
    save_participants(participants)
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)