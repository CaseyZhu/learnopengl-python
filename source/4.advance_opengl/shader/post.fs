#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D texture1;

/*void main()
{             
    FragColor = texture(texture1, TexCoords);
    float average = (FragColor.r + FragColor.g + FragColor.b) / 3.0;
    FragColor = vec4(average, average, average, 1.0);
}*/

const float offset = 1.0 / 300.0;  

void main()
{
    vec2 offsets[9] = vec2[](
        // 左上                 // 正上                  // 右上
        vec2(-offset,  offset), vec2( 0.0f,    offset),  vec2( offset,  offset), 
        // 左                  // 中                    // 右
        vec2(-offset,  0.0f),   vec2( 0.0f,    0.0f),   vec2( offset,  0.0f),   
        // 左下                // 正下                 // 右下
        vec2(-offset, -offset), vec2( 0.0f,   -offset), vec2( offset, -offset)  
    );
    //sharp
    float kernel[9] = float[](
        -1, -1, -1,
        -1,  9, -1,
        -1, -1, -1
    );
    //blur
    float kernel1[9] = float[](
    1.0 / 16, 2.0 / 16, 1.0 / 16,
    2.0 / 16, 4.0 / 16, 2.0 / 16,
    1.0 / 16, 2.0 / 16, 1.0 / 16  
    );
    //edge detect
    float kernel2[9] = float[](
         1,  1,  1,
         1, -8,  1,
         1,  1,  1
    );
    vec3 sampleTex[9];
    for(int i = 0; i < 9; i++)
    {
        sampleTex[i] = vec3(texture(texture1, TexCoords.st + offsets[i]));
    }
    vec3 col = vec3(0.0);
    for(int i = 0; i < 9; i++)
        col += sampleTex[i] * kernel2[i];

    FragColor = vec4(col, 1.0);
}
