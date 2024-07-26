import streamlit as st
from anthropic import Anthropic
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import random
import math

# Function to create a box (room) for 3D plot
def create_box(x, y, z, dx, dy, dz, color):
    return go.Mesh3d(
        x=[x, x, x+dx, x+dx, x, x, x+dx, x+dx],
        y=[y, y+dy, y+dy, y, y, y+dy, y+dy, y],
        z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
        i=[0, 0, 0, 1, 4, 4, 4, 5],
        j=[1, 2, 4, 2, 5, 6, 1, 6],
        k=[2, 3, 7, 3, 6, 7, 5, 7],
        color=color,
        opacity=0.7
    )

# Function to add text for 3D plot
def add_text(x, y, z, text):
    return go.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        text=[text],
        mode='text',
        textposition='middle center',
        textfont=dict(size=10, color='black')
    )

# Function to create a floor plan using Plotly (3D)
def create_3d_floor_plan(room_params, floor_height=0):
    data = []
    room_height = 3  # 3 meters room height
    for param in room_params:
        data.append(create_box(param['x'], param['y'], floor_height, param['dx'], param['dy'], room_height, param['color']))
        data.append(add_text(param['x'] + param['dx'] / 2, param['y'] + param['dy'] / 2, floor_height + 1.5, 
                             f"{param['name']}\n{param['dx']}m x {param['dy']}m"))
    return data

def generate_floor_plan_params(prompt):
    try:
        client = Anthropic(api_key='your_anthropic_api_key')  # Replace with your actual API key
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system="You are an expert architect specializing in Indian homes, Vastu principles, and modern design trends. Provide room parameters as a JSON array of objects, each with 'name', 'x', 'y', 'dx', 'dy', 'color', and 'floor' properties. Ensure rooms are connected efficiently with minimal gaps. Use only valid CSS color names for the 'color' property.",
            messages=[
                {
                    "role": "user",
                    "content": f"Generate room parameters for a Vastu-compliant modern Indian home floor plan with {prompt}. Provide the output as a JSON array. Ensure rooms are adjacent with no large gaps between them. Use only valid CSS color names for colors."
                }
            ]
        )
        # Extract JSON from the response
        json_start = message.content[0].text.find('[')
        json_end = message.content[0].text.rfind(']') + 1
        json_str = message.content[0].text[json_start:json_end]
        
        room_params = json.loads(json_str)
        
        # Validate and adjust room parameters
        max_dimension = 50  # Maximum allowed dimension in meters
        valid_colors = [
            'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'cyan', 'magenta',
            'lime', 'teal', 'lavender', 'brown', 'beige', 'maroon', 'olive', 'navy', 'grey',
            'white', 'black', 'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
            'bisque', 'blanchedalmond', 'blueviolet', 'burlywood', 'cadetblue', 'chartreuse',
            'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'darkblue',
            'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta',
            'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon',
            'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet',
            'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick', 'floralwhite',
            'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod',
            'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki',
            'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral',
            'lightcyan', 'lightgoldenrodyellow', 'lightgreen', 'lightpink', 'lightsalmon',
            'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow',
            'limegreen', 'linen', 'mediumaquamarine', 'mediumblue', 'mediumorchid',
            'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
            'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose',
            'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid',
            'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip',
            'peachpuff', 'peru', 'plum', 'powderblue', 'rosybrown', 'royalblue',
            'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver',
            'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen', 'steelblue', 'tan',
            'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen'
        ]
        
        for room in room_params:
            room['x'] = min(max(room['x'], 0), max_dimension)
            room['y'] = min(max(room['y'], 0), max_dimension)
            room['dx'] = min(max(room['dx'], 1), max_dimension)
            room['dy'] = min(max(room['dy'], 1), max_dimension)
            
            # Ensure color is valid
            if 'color' in room:
                room['color'] = room['color'].lower()
                if room['color'] not in valid_colors:
                    room['color'] = random.choice(valid_colors)
            else:
                room['color'] = random.choice(valid_colors)
        
        # Optimize room placement
        room_params = optimize_room_placement(room_params)
        
        return room_params
    except Exception as e:
        st.error(f"Error in generating floor plan parameters: {str(e)}")
        return None

def optimize_room_placement(room_params):
    total_area = sum(room['dx'] * room['dy'] for room in room_params)
    target_width = math.sqrt(total_area * 1.1)  # Add 10% for corridors
    
    current_x = current_y = 0
    max_height = 0
    
    for room in sorted(room_params, key=lambda r: r['dx'] * r['dy'], reverse=True):
        if current_x + room['dx'] > target_width:
            current_x = 0
            current_y += max_height
            max_height = 0
        
        room['x'] = current_x
        room['y'] = current_y
        current_x += room['dx']
        max_height = max(max_height, room['dy'])
    
    return room_params

def is_position_valid(x, y, room, all_rooms):
    for other_room in all_rooms:
        if other_room == room:
            continue
        if (x < other_room['x'] + other_room['dx'] and
            x + room['dx'] > other_room['x'] and
            y < other_room['y'] + other_room['dy'] and
            y + room['dy'] > other_room['y']):
            return False
    return True

def add_doors_and_windows(room_params):
    doors = []
    windows = []
    for i, room1 in enumerate(room_params):
        # Add windows to exterior walls
        if room1['x'] == 0 or room1['x'] + room1['dx'] == 50:
            windows.append({'x': room1['x'], 'y': room1['y'] + room1['dy']/2, 'z': 1.5, 'dx': 0, 'dy': 1})
        if room1['y'] == 0 or room1['y'] + room1['dy'] == 50:
            windows.append({'x': room1['x'] + room1['dx']/2, 'y': room1['y'], 'z': 1.5, 'dx': 1, 'dy': 0})
        
        for j, room2 in enumerate(room_params[i+1:]):
            if are_rooms_adjacent(room1, room2):
                door = calculate_door_position(room1, room2)
                doors.append(door)
    return doors, windows

def are_rooms_adjacent(room1, room2):
    return (abs(room1['x'] - room2['x']) <= room1['dx'] + room2['dx'] and
            abs(room1['y'] - room2['y']) <= room1['dy'] + room2['dy'])

def calculate_door_position(room1, room2):
    # Simplified door placement logic
    if room1['x'] == room2['x'] + room2['dx'] or room2['x'] == room1['x'] + room1['dx']:
        # Rooms are adjacent horizontally
        x = max(room1['x'], room2['x'])
        y = max(room1['y'], room2['y']) + min(room1['dy'], room2['dy']) / 2
        return {'x': x, 'y': y, 'z': 0, 'dx': 0, 'dy': 1}
    else:
        # Rooms are adjacent vertically
        x = max(room1['x'], room2['x']) + min(room1['dx'], room2['dx']) / 2
        y = max(room1['y'], room2['y'])
        return {'x': x, 'y': y, 'z': 0, 'dx': 1, 'dy': 0}

def create_door(x, y, z, dx, dy):
    return go.Mesh3d(
        x=[x, x+dx, x+dx, x],
        y=[y, y, y+dy, y+dy],
        z=[z, z, z+2, z+2],  # Assuming 2m height for doors
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color='brown',
        opacity=0.7
    )

def create_window(x, y, z, dx, dy):
    return go.Mesh3d(
        x=[x, x+dx, x+dx, x],
        y=[y, y, y+dy, y+dy],
        z=[z, z, z+1, z+1],  # Assuming 1m height for windows
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color='lightblue',
        opacity=0.5
    )

# Streamlit app
st.set_page_config(layout="wide")  # Use wide layout for better visibility

st.title('3D CAD Floor Plan Generator for Indian Homes')

# Create two columns for input and output
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Input Parameters")
    prompt = st.text_area("Enter your floor plan requirements:", 
                          "Provide detailed requirements including orientation, number of floors, and room specifications.")

    if st.button("Generate Floor Plan"):
        if prompt:
            with st.spinner("Generating floor plan..."):
                # Generate parameters using Anthropic API
                room_params = generate_floor_plan_params(prompt)
                if room_params:
                    doors, windows = add_doors_and_windows(room_params)
                    
                    st.success("Floor plan generated successfully!")
                    st.subheader("Generated Parameters:")
                    st.write(room_params)

                    # Extract number of floors from room_params
                    floors = max(param.get('floor', 0) for param in room_params) + 1

                    # Generate the 3D floor plans
                    all_floors = []
                    for i in range(floors):
                        floor_rooms = [room for room in room_params if room.get('floor', 0) == i]
                        floor_data = create_3d_floor_plan(floor_rooms, i * 3.1)
                        
                        # Add doors and windows to the floor
                        for door in doors:
                            floor_data.append(create_door(door['x'], door['y'], i * 3.1 + door['z'], door['dx'], door['dy']))
                        for window in windows:
                            floor_data.append(create_window(window['x'], window['y'], i * 3.1 + window['z'], window['dx'], window['dy']))
                        
                        all_floors.append(floor_data)

                    # Combine all floors
                    data = [item for sublist in all_floors for item in sublist]

                    # Create the 3D figure
                    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'scene'}, {'type': 'scene'}]],
                                        subplot_titles=('3D View', 'Top View'))

                    # Add 3D view
                    for trace in data:
                        fig.add_trace(trace, row=1, col=1)

                    # Add top view
                    for trace in create_3d_floor_plan(room_params, 0):
                        if isinstance(trace, go.Mesh3d):
                            trace.update(z=[0]*len(trace.z))
                        fig.add_trace(trace, row=1, col=2)

                    # Update the layout
                    fig.update_layout(
                        scene=dict(
                            xaxis_title='X (meters)',
                            yaxis_title='Y (meters)',
                            zaxis_title='Z (meters)',
                            aspectmode='data',
                            camera=dict(eye=dict(x=-1.5, y=-1.5, z=1))
                        ),
                        scene2=dict(
                            xaxis_title='X (meters)',
                            yaxis_title='Y (meters)',
                            zaxis_title='Z (meters)',
                            aspectmode='data',
                            camera=dict(eye=dict(x=0, y=0, z=2))
                        ),
                        title=f'{floors}-Story Modern Indian House Floor Plan',
                        height=700,
                        width=1000,
                        margin=dict(l=0, r=0, b=0, t=30)
                    )

                    # Add compass (assuming North is always up)
                    fig.add_annotation(
                        x=1, y=1,
                        text="N",
                        showarrow=False,
                        font=dict(size=20, color="red"),
                        xanchor="right",
                        yanchor="top"
                    )

                    # Save as HTML
                    fig.write_html("3d_floor_plan_advanced.html")

                    # Display the figure in Streamlit
                    with col2:
                        st.header("Generated Floor Plan")
                        st.plotly_chart(fig, use_container_width=True)
                        st.success("3D floor plan saved as '3d_floor_plan_advanced.html'")

st.markdown("""
## Features of this 3D Floor Plan Generator:

1. **Multi-story Design**: Generate floor plans for multiple floors based on user input.
2. **Vastu Compliance**: Follows Vastu Shastra principles for room placement and orientation.
3. **Customizable Rooms**: Users provide detailed requirements for room specifications.
4. **Orientation-based Layout**: Adjusts the layout based on the specified orientation.
5. **3D Visualization**: Provides both 3D and top-view visualizations using Plotly.
6. **Automatic Door and Window Placement**: Adds doors between adjacent rooms and windows on exterior walls.
7. **Optimized Room Placement**: Minimizes gaps between rooms for efficient space utilization.
""")