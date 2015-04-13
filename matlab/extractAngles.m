function [ data ] = extractAngles( trip )
%EXTRACTANGLES extract angles from a trip

	data = zeros(1, size(trip, 1));
	for iter = 2 : size(trip, 1) - 1
		 P1 = trip(iter - 1, :);
		 P2 = trip(iter, :);
		 P3 = trip(iter + 1, :);
		 angle = atan2((det([P3 - P1; P2 - P1])), dot(P3 - P1, P2 - P1)) * 180 / pi;
		 data(iter) = angle;
	end
end

