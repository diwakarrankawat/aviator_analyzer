import streamlit as st

st.title('Data Analyzer')

if not st.session_state.keys():
    st.session_state.update({
        'checks': [],
        'bets': [],
        'reset': False,
        'starting_balance': 0.0,
    })
# st.session_state

st.write("## General Config")
st.session_state['starting_balance'] = st.number_input("Starting Balance:", min_value=0.0, step=0.01, value=st.session_state['starting_balance'])

def add_strategy(multiplier, condition):
    st.session_state['checks'].append({'multiplier': multiplier, 'condition': condition})

def conditions():
    st.write("## Checks")

    multiplier = st.number_input("Enter multiplier (float):", format="%.2f", min_value=1.00, step=0.01)
    condition = st.selectbox("Select condition:", ["greater than", "less than"])

    st.button("Add condition", on_click=lambda : add_strategy(multiplier, condition))

    # Display all strategies
    if st.session_state['checks']:
        st.write("Conditions:")
        with st.expander('Conditions'):
            for s_no, data in enumerate(st.session_state['checks']):
            # chip = f"{ '<' if condition['condition'] == 'greater than' else '>'} {condition['multiplier']}x"
                chip = f"{data['condition']} {data['multiplier']}x"
                col1, col2 = st.columns(2)
                col1.write(f"{s_no+1}. {chip}")
                col2.button("Delete", on_click=lambda s_no=s_no: st.session_state['checks'].pop(s_no), key=s_no)

def bets():
    st.write("## Bets")

    col1, col2 = st.columns(2)
    bet = col1.number_input("Bet Amount:", min_value=10.0, step=0.01, max_value=8000.0)
    multiplier = col2.number_input("Checkout At:", format="%.2f", min_value=1.00, step=0.01, max_value=10000.0, value=2.00)
    st.button("Add bet", on_click=lambda : st.session_state['bets'].append({
        "amount": bet,
        "checkout": multiplier,
    }))
    st.checkbox("Reset on win", value=st.session_state['reset'], on_change=lambda: st.session_state.update({'reset': not st.session_state['reset']}))

    # Display all bets
    if st.session_state['bets']:
        st.write("Bets:")
        with st.expander('Bets'):
            for s_no, _bet in enumerate(st.session_state['bets']):
                col1, col2 = st.columns(2)
                col1.write(f"{s_no+1}. {_bet['amount']} @ {_bet['checkout']}x")
                col2.button("Delete", on_click=lambda s_no=s_no: st.session_state['bets'].pop(s_no), key=f'{s_no}b')

def processor(data: list[float]):
    balance = st.session_state['starting_balance'] or 1000.0
    condition_at = 0
    betting_at = 0
    records = []
    for x in data:
        should_bet = condition_at == len(st.session_state['checks'])
        rec ={
            'balance': balance,
            'x': x,
            'bet': (st.session_state['bets'][betting_at]['amount'] if should_bet else 0.0) if len(st.session_state['bets']) > betting_at else 0.0,
            'checkout': (st.session_state['bets'][betting_at]['checkout'] if should_bet else 0.0) if len(st.session_state['bets']) > betting_at else 0.0,
            'satisfied': condition_at,
            'betting_try': betting_at,
        }
        records.append(rec)
        if not should_bet:
            if st.session_state['checks'][condition_at]['condition'] == "greater than":
                satisfied = x > st.session_state['checks'][condition_at]['multiplier']
            else:
                satisfied = x < st.session_state['checks'][condition_at]['multiplier']
            if satisfied:
                condition_at += 1
                continue
            elif condition_at > 0:
                condition_at = 0
            else:
                continue
        else:
            if not betting_at < len(st.session_state['bets']):
                betting_at = 0
                condition_at = 0
                continue
            balance -= st.session_state['bets'][betting_at]['amount']
            if x > st.session_state['bets'][betting_at]['checkout']:
                balance += st.session_state['bets'][betting_at]['amount'] * st.session_state['bets'][betting_at]['checkout']
                if st.session_state['reset']:   
                    condition_at = 0
                    betting_at = 0
            betting_at += 1
    return records


def data_process():
    st.write("## Data")

    file = st.file_uploader("Upload file:", type=["csv"])
    st.write("Instructions: Upload file containing header \"x\" for the multiplier. The file should be in .csv format.")

    if file:
        import pandas as pd
        df = pd.read_csv(file)
        df = df.dropna()
        df = df.reset_index(drop=True)
        df['x'] = df['x'].astype(float)

        st.write("Data Preview:")
        records = processor(df['x'].tolist())
        st.line_chart(
            pd.DataFrame(records)['balance']
        )
        st.dataframe(pd.DataFrame(records))


conditions()
bets()
data_process()