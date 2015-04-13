function [ data ] = smoothData( input, peaks, freqs )
%SMOOTHDATA smooth signal, cut out peaks

	data = input(abs(input) < peaks); % cut out corners bigger than 50 degrees
	n = length(data);
	f = fft(data);
	f(floor(n / 2) + 1 - freqs:floor(n / 2) + freqs) = zeros(freqs * 2, 1); % cut out high frequencies
	data = real(ifft(f));

end

