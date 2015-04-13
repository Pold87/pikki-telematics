function [ ret ] = rotate( trip )
%ROTATE Rotate trip to y = 0
    ret = [];
    endpoint = trip(end,:);
    alpha = - atan2(endpoint(2), endpoint(1));
    
    rot_matrix = [ cos(alpha), -sin(alpha) ; sin(alpha), cos(alpha) ];
    
    for iter = 1 : size(trip,1)
        ret = [ret ; (rot_matrix * trip(iter, :)')'];
    end

end

