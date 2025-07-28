import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# สร้าง Dash app
app = dash.Dash(__name__)

# โหลดข้อมูล
def load_data():
    try:
        df = pd.read_csv('cost.csv')
        # ทำความสะอาดข้อมูล
        df.columns = df.columns.str.strip()
        df['มหาวิทยาลัย'] = df['มหาวิทยาลัย'].fillna('').str.strip()
        df['Keyword'] = df['Keyword'].fillna('').str.strip()
        df['ค่าใช้จ่าย'] = pd.to_numeric(df['ค่าใช้จ่าย'], errors='coerce').fillna(0)
        df['ประเภทหลักสูตร'] = df['ประเภทหลักสูตร'].fillna('').str.strip()
        
        # เพิ่มคอลัมน์ภูมิภาค
        df['ภูมิภาค'] = df['มหาวิทยาลัย'].apply(get_region)
        
        # กรองข้อมูลที่มีค่าใช้จ่าย > 0
        df = df[(df['มหาวิทยาลัย'] != '') & (df['ค่าใช้จ่าย'] > 0)]
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def get_region(university_name):
    if pd.isna(university_name):
        return 'ภาคกลาง'
    
    university_name = str(university_name)
    if any(keyword in university_name for keyword in ['เชียงใหม่', 'แม่ฟ้าหลวง', 'พะเยา', 'นเรศวร']):
        return 'ภาคเหนือ'
    elif any(keyword in university_name for keyword in ['ขอนแก่น', 'สุรนารี', 'อุบลราชธานี', 'กาฬสินธุ์', 'นครพนม', 'ราชมงคลอีสาน']):
        return 'ภาคอีสาน'
    elif any(keyword in university_name for keyword in ['สงขลานครินทร์', 'วลัยลักษณ์', 'นราธิวาสราชนครินทร์', 'ราชมงคลศรีวิชัย']):
        return 'ภาคใต้'
    else:
        return 'ภาคกลาง'

# โหลดข้อมูล
df = load_data()

# สร้าง layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("📊 Dashboard ค่าใช้จ่ายหลักสูตรวิศวกรรมคอมพิวเตอร์และปัญญาประดิษฐ์", 
                className="text-4xl font-bold text-center mb-2"),
        html.P("วิเคราะห์ข้อมูลค่าเทอมในมหาวิทยาลัยต่างๆในประเทศไทย ข้อมูลจากเว็บไซต์ TCAS",
               className="text-center text-gray-600 mb-8")
    ], className="text-center mb-8"),
    
    # Filters
    html.Div([
        html.H2("🔍 ตัวกรอง", className="text-xl font-semibold mb-4"),
        html.Div([
            html.Div([
                html.Label("หลักสูตร", className="block text-sm font-medium mb-2"),
                dcc.Dropdown(
                    id='keyword-dropdown',
                    options=[{'label': 'ทั้งหมด', 'value': 'all'}] + 
                           [{'label': k, 'value': k} for k in sorted(df['Keyword'].unique())],
                    value='all',
                    className="w-full"
                )
            ], className="md:col-span-1"),
            
            html.Div([
                html.Label("ประเภทหลักสูตร", className="block text-sm font-medium mb-2"),
                dcc.Dropdown(
                    id='type-dropdown',
                    options=[{'label': 'ทั้งหมด', 'value': 'all'}] + 
                           [{'label': t, 'value': t} for t in sorted(df['ประเภทหลักสูตร'].unique())],
                    value='all',
                    className="w-full"
                )
            ], className="md:col-span-1"),
            
            html.Div([
                html.Label("ภูมิภาค", className="block text-sm font-medium mb-2"),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': 'ทั้งหมด', 'value': 'all'}] + 
                           [{'label': r, 'value': r} for r in sorted(df['ภูมิภาค'].unique())],
                    value='all',
                    className="w-full"
                )
            ], className="md:col-span-1"),
        ], className="grid grid-cols-1 md:grid-cols-3 gap-4")
    ], className="bg-white rounded-lg shadow-lg p-6 mb-6"),
    
    # Statistics Cards
    html.Div([
        html.Div([
            html.Div(id="stat-count", className="text-3xl font-bold text-blue-600"),
            html.Div("จำนวนหลักสูตร", className="text-gray-600")
        ], className="bg-white rounded-lg shadow-lg p-6 text-center"),
        
        html.Div([
            html.Div(id="stat-average", className="text-3xl font-bold text-green-600"),
            html.Div("ค่าใช้จ่ายเฉลี่ย", className="text-gray-600")
        ], className="bg-white rounded-lg shadow-lg p-6 text-center"),
        
        html.Div([
            html.Div(id="stat-min", className="text-3xl font-bold text-red-600"),
            html.Div("ต่ำสุด", className="text-gray-600")
        ], className="bg-white rounded-lg shadow-lg p-6 text-center"),
        
        html.Div([
            html.Div(id="stat-max", className="text-3xl font-bold text-purple-600"),
            html.Div("สูงสุด", className="text-gray-600")
        ], className="bg-white rounded-lg shadow-lg p-6 text-center"),
        
        html.Div([
            html.Div(id="stat-median", className="text-3xl font-bold text-orange-600"),
            html.Div("ค่ากลาง", className="text-gray-600")
        ], className="bg-white rounded-lg shadow-lg p-6 text-center"),
    ], className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6"),
    
    # Charts Grid
    html.Div([
        # Cost Range Distribution
        html.Div([
            html.H3("การกระจายตัวของค่าใช้จ่าย", className="text-lg font-semibold mb-4"),
            html.Div([
                dcc.Graph(id='cost-range-chart', style={'height': '400px'})
            ], style={'height': '400px'})
        ], className="bg-white rounded-lg shadow-lg p-6"),
        
        # Course Type Distribution
        html.Div([
            html.H3("สัดส่วนประเภทหลักสูตร", className="text-lg font-semibold mb-4"),
            html.Div([
                dcc.Graph(id='type-distribution-chart', style={'height': '400px'})
            ], style={'height': '400px'})
        ], className="bg-white rounded-lg shadow-lg p-6"),
    ], className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"),
    
    # Top Expensive Universities
    html.Div([
        html.H3("🏆 มหาวิทยาลัยที่มีค่าใช้จ่ายสูงสุด (Top 10)", className="text-lg font-semibold mb-4"),
        html.Div(id='top-expensive-table')
    ], className="bg-white rounded-lg shadow-lg p-6 mb-6"),
    
    # Footer
    html.Div([
        html.Span(id="footer-text", className="text-gray-500 text-sm")
    ], className="text-center")
    
], className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6 max-w-7xl mx-auto")

# Callback สำหรับการอัพเดทข้อมูลตาม filter
@app.callback(
    [Output('stat-count', 'children'),
     Output('stat-average', 'children'),
     Output('stat-min', 'children'),
     Output('stat-max', 'children'),
     Output('stat-median', 'children'),
     Output('cost-range-chart', 'figure'),
     Output('type-distribution-chart', 'figure'),
     Output('top-expensive-table', 'children'),
     Output('footer-text', 'children')],
    [Input('keyword-dropdown', 'value'),
     Input('type-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_dashboard(selected_keyword, selected_type, selected_region):
    # กรองข้อมูล
    filtered_df = df.copy()
    
    if selected_keyword != 'all':
        filtered_df = filtered_df[filtered_df['Keyword'] == selected_keyword]
    
    if selected_type != 'all':
        filtered_df = filtered_df[filtered_df['ประเภทหลักสูตร'] == selected_type]
    
    if selected_region != 'all':
        filtered_df = filtered_df[filtered_df['ภูมิภาค'] == selected_region]
    
    # คำนวณสถิติ
    if len(filtered_df) == 0:
        stats = {'count': 0, 'average': 0, 'min': 0, 'max': 0, 'median': 0}
    else:
        costs = filtered_df['ค่าใช้จ่าย'].values
        stats = {
            'count': len(filtered_df),
            'average': int(costs.mean()),
            'min': int(costs.min()),
            'max': int(costs.max()),
            'median': int(np.median(costs))
        }
    
    # ฟอร์แมตสถิติ
    def format_currency(value):
        if value == 0:
            return '-'
        return f"฿{value:,}"
    
    stat_count = str(stats['count'])
    stat_average = format_currency(stats['average'])
    stat_min = format_currency(stats['min'])
    stat_max = format_currency(stats['max'])
    stat_median = format_currency(stats['median'])
    
    # สร้างกราฟการกระจายตัวของค่าใช้จ่าย
    cost_ranges = [
        {'name': '< 20,000', 'min': 0, 'max': 19999},
        {'name': '20,000-30,000', 'min': 20000, 'max': 30000},
        {'name': '30,001-50,000', 'min': 30001, 'max': 50000},
        {'name': '50,001-70,000', 'min': 50001, 'max': 70000},
        {'name': '> 70,000', 'min': 70001, 'max': float('inf')}
    ]
    
    range_data = []
    for range_info in cost_ranges:
        count = len(filtered_df[
            (filtered_df['ค่าใช้จ่าย'] >= range_info['min']) & 
            (filtered_df['ค่าใช้จ่าย'] <= range_info['max'])
        ])
        range_data.append({'name': range_info['name'], 'count': count})
    
    cost_range_fig = px.bar(
        pd.DataFrame(range_data),
        x='name', y='count',
        title="",
        labels={'name': 'ช่วงค่าใช้จ่าย', 'count': 'จำนวน'},
        color_discrete_sequence=['#FFD700']
    )
    cost_range_fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis_title="ช่วงค่าใช้จ่าย",
        yaxis_title="จำนวน"
    )
    
    # สร้างกราฟสัดส่วนประเภทหลักสูตร
    if len(filtered_df) > 0:
        type_counts = filtered_df['ประเภทหลักสูตร'].value_counts()
        type_distribution_fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title=""
        )
        type_distribution_fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
    else:
        type_distribution_fig = px.pie(values=[], names=[], title="")
        type_distribution_fig.update_layout(
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
    
    # สร้างตาราง Top 10
    if len(filtered_df) > 0:
        top_10 = filtered_df.nlargest(10, 'ค่าใช้จ่าย')
        
        table_data = []
        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            table_data.append({
                'อันดับ': i,
                'มหาวิทยาลัย': row['มหาวิทยาลัย'][:50] + ('...' if len(row['มหาวิทยาลัย']) > 50 else ''),
                'หลักสูตร': row['Keyword'],
                'ประเภท': row['ประเภทหลักสูตร'],
                'ภูมิภาค': row['ภูมิภาค'],
                'ค่าใช้จ่าย': f"฿{row['ค่าใช้จ่าย']:,}"
            })
        
        table = dash_table.DataTable(
            data=table_data,
            columns=[
                {'name': 'อันดับ', 'id': 'อันดับ'},
                {'name': 'มหาวิทยาลัย', 'id': 'มหาวิทยาลัย'},
                {'name': 'หลักสูตร', 'id': 'หลักสูตร'},
                {'name': 'ประเภท', 'id': 'ประเภท'},
                {'name': 'ภูมิภาค', 'id': 'ภูมิภาค'},
                {'name': 'ค่าใช้จ่าย', 'id': 'ค่าใช้จ่าย'}
            ],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    else:
        table = html.Div("ไม่มีข้อมูลที่จะแสดง", className="text-center text-gray-500")
    
    # Footer text
    footer_text = f"📈 Dashboard สร้างจากข้อมูล {len(df)} หลักสูตร | ข้อมูลที่แสดง: {len(filtered_df)} หลักสูตร"
    
    return (stat_count, stat_average, stat_min, stat_max, stat_median,
            cost_range_fig, type_distribution_fig, table, footer_text)

# เพิ่ม CSS สำหรับ Tailwind-like styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
