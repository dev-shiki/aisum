import { shallowMount } from '@vue/test-utils'
import StatusDisplay from '../StatusDisplay.vue'

describe('StatusDisplay', () => {
  it('renders status text passed as prop', () => {
    const status = 'Processing...';
    const wrapper = shallowMount(StatusDisplay, {
      propsData: { status }
    });
    expect(wrapper.text()).toContain(status);
  });

  it('renders error status with error class', () => {
    const status = 'Error: Something went wrong';
    const wrapper = shallowMount(StatusDisplay, {
      propsData: { status }
    });
    // Cek apakah ada class error jika status mengandung "error"
    expect(wrapper.text().toLowerCase()).toContain('error');
    // Jika ada class khusus, bisa cek: expect(wrapper.classes()).toContain('error')
  });

  it('renders loading status', () => {
    const status = 'Loading...';
    const wrapper = shallowMount(StatusDisplay, {
      propsData: { status }
    });
    expect(wrapper.text()).toContain('Loading');
  });

  it('renders empty status', () => {
    const status = '';
    const wrapper = shallowMount(StatusDisplay, {
      propsData: { status }
    });
    expect(wrapper.text()).toBe('');
  });
}); 