from pycatia import catia
import google.generativeai as genai
from pycatia.scripts.vba import vba_nothing
from pycatia.mec_mod_interfaces.part import Part
from pycatia.mec_mod_interfaces.part_document import PartDocument


test = catia()
document = PartDocument(test.active_document.com_object)
part = Part(document.part.com_object)
hsf = part.hybrid_shape_factory

hybrid_shape_factory = part.hybrid_shape_factory
part_shape_factory = part.shape_factory
body = part.main_body

hybrid_bodies = part.hybrid_bodies
hybrid_body_points = hybrid_bodies.add()
hybrid_body_shape = hybrid_bodies.add()
hybrid_body_surface = hybrid_bodies.add()
hybrid_body_points.name = "points"
hybrid_body_shape.name = "shapes"
hybrid_body_surface.name = "construction_surfaces"


genai.configure(api_key="AIzaSyAtm4G9bZR91PTMXAw0jv6CY7lgR-dVjjo")

generation_config = {
 "temperature": 0.2,
 "top_p": 1,
 "top_k": 1,
 "max_output_tokens": 400,
}

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
 generation_config=generation_config)


convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["for any given sentence give me directly the extracted info separated by commas without any description or any axplanation in the same line use this template for the extraction : shape, radius, height, x coordinates, y coordinates, z coordinates, plan, axis , don't skip any info and if the info doesn't exist write None and "]
  },
  {
    "role": "model",
    "parts": ["cylinder, 20, 200, 1, 2, 2, None, Y"]
  },
  {
    "role": "user",
    "parts": ["Form a circle centered at (500, 100, -400) with a radius of 20."]
  },
  {
    "role": "model",
    "parts": ["circle, 20, None, 500, 100, -400, None, None"]
  },
  {
    "role": "user",
    "parts": ["Create a sphere with radius 35 at (200, 400, -200)."]
  },
  {
    "role": "model",
    "parts": ["sphere, 35, None, 200, 400, -200, None, None"]
  },
  {
    "role": "user",
    "parts": ["Make a circle with a radius of 18 at (700, -200, -300).\nGenerate a cylinder at (100, -100, 0) having height 45 and radius 20."]
  },
  {
    "role": "model",
    "parts": ["circle, 18, None, 700, -200, -300, None, None\ncylinder, 20, 45, 100, -100, 0, None, None"]
  },
])


while True:
 
 choice = input("Enter 'draw' to continue drawing, 'list' to list the shapes, 'select' to select a specific shape: ")
 if choice.lower() == 'draw':
    text = "for any given sentence give me directly the extracted info separated by commas without any description or any axplanation in the same line using this template for the extraction : shape, radius, height, x coordinates, y coordinates, z coordinates, plan, axis and if the info doesn't exist write None and if either axis or height or plan don't exist return None, else skip:"
    input_text = input("extract the geometrique informations from the sentences :")
    convo.send_message(text + input_text)
    response = convo.last.text


    info_parts = response.split(', ')
    shape = info_parts[0].strip()
    radius = info_parts[1].strip()
    height = info_parts[2].strip()
    center_x = info_parts[3].strip()
    center_y = info_parts[4].strip()
    center_z = info_parts[5].strip()
    plan = info_parts[6].strip()
    axis = info_parts[7].strip()


    print(shape)
    print(radius)
    print(height)
    print(float(center_x), float(center_y), float(center_z))
    print(axis)
    print(plan)


    point_origin = hybrid_shape_factory.add_new_point_coord(float(center_x), float(center_y), float(center_z))
    line_YZ = hybrid_shape_factory.add_new_line_normal(part.origin_elements.plane_yz, point_origin, 0, 10, True)
    direction_YZ = hsf.add_new_direction(line_YZ)
 

    if shape.lower() == "circle" :
      circle = hybrid_shape_factory.add_new_circle_center_axis(direction_YZ, point_origin, radius, True)
      hybrid_body_shape.append_hybrid_shape(circle)
    elif shape.lower() == "cylinder" :
      cylinder = hybrid_shape_factory.add_new_cylinder(point_origin, radius, 0, height, direction_YZ)
      hybrid_body_shape.append_hybrid_shape(cylinder)
    elif shape.lower() == "sphere" :
      sphere = hybrid_shape_factory.add_new_sphere(point_origin, vba_nothing, radius, -360, 360, -360, 360)
      hybrid_body_shape.append_hybrid_shape(sphere)
    elif shape.lower() == "point" :
      point = hybrid_shape_factory.add_new_point_coord(center_x, center_y, center_z)
      hybrid_body_points.append_hybrid_shape(point)
    else :
     print("unsupported shape type :", shape)

    part.update()


 elif choice.lower() == 'list':
        for hybrid_body in hybrid_bodies:
            if hybrid_body.hybrid_shapes:
                print(f"hybrid body : {hybrid_body.name}")
                for i, hybrid_shape in enumerate(hybrid_body.hybrid_shapes):
                    print(f" {i + 1}. : {hybrid_shape.name}")
 elif choice.lower() == 'select':
    hybrid_body_dict = {}
    for hybrid_body in hybrid_bodies:
        if hybrid_body.hybrid_shapes:
            print(f"hybrid body : {hybrid_body.name}")
            hybrid_body_dict[hybrid_body.name] = hybrid_body.hybrid_shapes

    selected_hybrid_body = input("Enter the name of the hybrid body: ")
    if selected_hybrid_body in hybrid_body_dict:
        hybrid_shapes = hybrid_body_dict[selected_hybrid_body]
        for i, hybrid_shape in enumerate(hybrid_shapes):
            print(f" {i + 1}. : {hybrid_shape.name}")

        index_input = input("Enter the index of the shape: ")
        if index_input.isdigit():
            index = int(index_input) - 1
            if 0 <= index < len(hybrid_shapes):
                selected_shape = hybrid_shapes[index]
                print(f"Selected shape: {selected_shape.name}")
                # Do whatever you want with the selected shape here
                
            else:
                print("Invalid index.")
        else:
            print("Invalid input. Please enter a number.")
    else:
        print("Invalid input. Please enter a number.")
 else:
        print("Invalid choice. Please enter 'draw', 'list', or 'select'.")
